"""
主程序入口
整合所有模块，实现完整的教授信息爬取流程
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# 添加 Web_analys 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "Web_analys"))
# 添加 utils 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from Web_analys.config_manager import ConfigManager
from Web_analys.BrowserManager import ChromeManager, EdgeManager
from Web_analys.discovery import SeedManager
from Web_analys.scheduler import TaskManager, TaskType, TaskPriority, RetryStrategy
from Web_analys.fetcher import FetcherFactory
from Web_analys.parser import ParserFactory
from Web_analys.normalization import (
    FieldNormalizer, NameParser, EmailRestorer,
    EntityDeduplicator, DepartmentMapper
)
from Web_analys.storage import StorageManager
from Web_analys.update import IncrementalUpdater, VersionManager
from utils import clean_output_dir


def setup_logger(name: str, log_dir: str) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 文件 handler
    log_file = log_path / f"{name}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def _validate_faculty_entry(faculty_info: Dict[str, Any], logger: logging.Logger) -> bool:
    """
    验证faculty条目是否有效
    
    Args:
        faculty_info: faculty信息
        logger: 日志记录器
        
    Returns:
        bool: 是否有效
    """
    # 必须有姓名
    name = faculty_info.get('name', '').strip()
    if not name or len(name) < 2 or len(name) > 50:
        logger.debug(f"验证失败：姓名无效: {name}")
        return False
    
    # 验证email格式（如果有）
    email = faculty_info.get('email', '').strip()
    if email:
        import re
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(email_pattern, email):
            logger.debug(f"验证失败：email格式无效: {email}")
            return False
    
    # 验证title（如果有）
    title = faculty_info.get('title', '').strip()
    if title:
        # title应该是有效的职称，不应该太长
        if len(title) > 50:
            logger.debug(f"验证失败：title过长: {title}")
            return False
    
    return True


async def process_list_page_task(
    task,
    fetcher_factory: FetcherFactory,
    parser_factory: ParserFactory,
    storage_manager: StorageManager,
    normalizers: dict,
    incremental_updater: IncrementalUpdater,
    version_manager: VersionManager,
    logger: logging.Logger
) -> bool:
    """
    处理列表页任务
    
    Args:
        task: 任务对象
        fetcher_factory: 抓取器工厂
        parser_factory: 解析器工厂
        storage_manager: 存储管理器
        normalizers: 归一化器字典
        incremental_updater: 增量更新器
        version_manager: 版本管理器
        logger: 日志记录器
        
    Returns:
        bool: 是否处理成功
    """
    url = task.url
    metadata = task.metadata
    university = metadata.get('university')
    department = metadata.get('department')
    page_type = metadata.get('page_type', 'faculty_list')
    adapter_name = metadata.get('adapter')
    
    try:
        # 检查是否需要更新
        should_update_result = incremental_updater.should_update(url, page_type, university, department)
        logger.info(f"🔍 更新检查 - should_update: {should_update_result}, url: {url}")
        logger.info(f"   配置: force_update={incremental_updater.force_update}, "
                   f"enable_change_detection={incremental_updater.enable_change_detection}")
        
        if not should_update_result:
            logger.warning(f"⏸️  跳过更新（未到更新时间或force_update=false）: {url}")
            return True
        
        # 抓取页面
        logger.info(f"📥 抓取列表页: {url}")
        fetch_result = await fetcher_factory.fetch(url)
        
        if not fetch_result.success:
            logger.error(f"❌ 抓取失败: {url}")
            return False
        
        # 检查内容是否变化
        is_changed_result = incremental_updater.is_changed(fetch_result.html, url, university, department)
        logger.info(f"🔍 内容变化检查 - is_changed: {is_changed_result}, url: {url}")
        
        # 如果强制更新，即使内容未变化也要解析
        force_parse = incremental_updater.force_update
        
        if not is_changed_result and not force_parse:
            logger.info(f"📄 内容未变化且未启用强制更新，跳过解析但更新文件: {url}")
            # 即使内容未变化，也更新fetched_at时间（覆盖文件）
            logger.info(f"💾 保存原始页面（即使内容未变化）: {url}")
            storage_manager.save_raw(fetch_result, university, department)
            logger.info(f"✅ 文件已更新: {url}")
            return True
        elif not is_changed_result and force_parse:
            logger.info(f"🔄 内容未变化但强制更新模式，强制重新解析: {url}")
        
        # 保存原始页面
        raw_info = storage_manager.save_raw(fetch_result, university, department)
        
        # 解析页面
        logger.info(f"🔍 解析列表页: {url}")
        parsed_result = parser_factory.parse(fetch_result.html, url, adapter_name)
        
        if parsed_result.get('page_type') != 'faculty_list':
            logger.warning(f"⚠️  解析结果不是列表页类型: {url}, 类型: {parsed_result.get('page_type')}")
            return False
        
        # 保存版本
        version_manager.save_version(
            url, fetch_result.html, parsed_result,
            university, department
        )
        
        # 处理faculty列表
        faculty_list = parsed_result.get('data', {}).get('faculty_list', [])
        logger.info(f"📋 提取到 {len(faculty_list)} 个教授信息 (大学: {university}, 系: {department})")
        
        # 归一化和保存实体
        entities = []
        existing_entities = storage_manager.entity_storage.get_all()
        validated_count = 0
        skipped_count = 0
        
        for faculty_info in faculty_list:
            # 数据验证：检查条目是否有效
            if not _validate_faculty_entry(faculty_info, logger):
                skipped_count += 1
                logger.debug(f"❌ 跳过无效条目: {faculty_info.get('name', 'Unknown')}")
                continue
            validated_count += 1
            
            # 归一化
            entity = normalizers['field_normalizer'].normalize(faculty_info)
            
            # 解析姓名
            if 'name' in entity:
                name_info = normalizers['name_parser'].parse(entity['name'])
                entity.update(name_info)
            
            # 还原邮箱
            if 'email' in entity:
                email = normalizers['email_restorer'].restore(entity['email'])
                if email:
                    entity['email'] = email
            
            # 添加大学和部门信息
            entity['university'] = university
            entity['department'] = department
            
            # 改进去重逻辑：在生成ID前先检查重复
            duplicate = normalizers['entity_deduplicator'].find_duplicate(entity, existing_entities)
            
            if duplicate:
                # 合并实体，使用现有ID
                entity = normalizers['entity_deduplicator'].merge_entities(duplicate, entity)
                entity['id'] = duplicate.get('id')
                logger.debug(f"合并重复实体: {entity.get('name')} (ID: {entity['id']})")
            else:
                # 生成新ID
                entity['id'] = normalizers['entity_deduplicator'].generate_entity_id(entity)
                logger.debug(f"新实体: {entity.get('name')} (ID: {entity['id']})")
            
            entities.append(entity)
            # 更新existing_entities列表，避免同一批次内重复
            existing_entities.append(entity)
        
        # 保存实体前的统计
        logger.info(f"📊 处理统计 (大学: {university}, 系: {department}) - "
                   f"原始提取: {len(faculty_list)}, "
                   f"验证通过: {validated_count}, "
                   f"验证失败: {skipped_count}, "
                   f"最终保存: {len(entities)}")
        
        # 批量保存实体
        saved_count = storage_manager.entity_storage.save_batch(entities)
        logger.info(f"💾 保存 {saved_count} 个实体到数据库")
        
        # 保存关系
        for entity in entities:
            storage_manager.save_relations(entity)
        
        return True
        
    except Exception as e:
        logger.error(f"处理列表页任务失败: {url}, 错误: {e}", exc_info=True)
        return False


async def process_profile_page_task(
    task,
    fetcher_factory: FetcherFactory,
    parser_factory: ParserFactory,
    storage_manager: StorageManager,
    normalizers: dict,
    incremental_updater: IncrementalUpdater,
    version_manager: VersionManager,
    logger: logging.Logger
) -> bool:
    """
    处理个人页任务
    
    Args:
        task: 任务对象
        fetcher_factory: 抓取器工厂
        parser_factory: 解析器工厂
        storage_manager: 存储管理器
        normalizers: 归一化器字典
        incremental_updater: 增量更新器
        version_manager: 版本管理器
        logger: 日志记录器
        
    Returns:
        bool: 是否处理成功
    """
    url = task.url
    metadata = task.metadata
    university = metadata.get('university')
    department = metadata.get('department')
    page_type = 'profile'
    adapter_name = metadata.get('adapter')
    
    try:
        # 检查是否需要更新
        should_update_result = incremental_updater.should_update(url, page_type, university, department)
        logger.info(f"🔍 更新检查 - should_update: {should_update_result}, url: {url}")
        logger.info(f"   配置: force_update={incremental_updater.force_update}, "
                   f"enable_change_detection={incremental_updater.enable_change_detection}")
        
        if not should_update_result:
            logger.warning(f"⏸️  跳过更新（未到更新时间或force_update=false）: {url}")
            return True
        
        # 抓取页面
        logger.info(f"📥 抓取个人页: {url}")
        fetch_result = await fetcher_factory.fetch(url)
        
        if not fetch_result.success:
            logger.error(f"❌ 抓取失败: {url}")
            return False
        
        # 检查内容是否变化
        is_changed_result = incremental_updater.is_changed(fetch_result.html, url, university, department)
        logger.info(f"🔍 内容变化检查 - is_changed: {is_changed_result}, url: {url}")
        
        # 如果强制更新，即使内容未变化也要解析
        force_parse = incremental_updater.force_update
        
        if not is_changed_result and not force_parse:
            logger.info(f"📄 内容未变化且未启用强制更新，跳过解析但更新文件: {url}")
            # 即使内容未变化，也更新fetched_at时间（覆盖文件）
            logger.info(f"💾 保存原始页面（即使内容未变化）: {url}")
            storage_manager.save_raw(fetch_result, university, department)
            logger.info(f"✅ 文件已更新: {url}")
            return True
        elif not is_changed_result and force_parse:
            logger.info(f"🔄 内容未变化但强制更新模式，强制重新解析: {url}")
        
        # 保存原始页面
        logger.info(f"💾 保存原始页面（内容已变化或强制更新）: {url}")
        raw_info = storage_manager.save_raw(fetch_result, university, department)
        logger.info(f"✅ 原始页面已保存: {raw_info.get('html_path', 'N/A')}")
        
        # 解析页面
        logger.info(f"🔍 解析个人页: {url}")
        parsed_result = parser_factory.parse(fetch_result.html, url, adapter_name)
        
        if parsed_result.get('page_type') != 'profile':
            logger.warning(f"解析结果不是个人页类型: {url}")
            return False
        
        # 保存版本
        version_manager.save_version(
            url, fetch_result.html, parsed_result,
            university, department
        )
        
        # 归一化和保存实体
        entity = parsed_result.get('data', {})
        
        # 归一化
        entity = normalizers['field_normalizer'].normalize(entity)
        
        # 解析姓名
        if 'name' in entity:
            name_info = normalizers['name_parser'].parse(entity['name'])
            entity.update(name_info)
        
        # 还原邮箱
        if 'email' in entity:
            email = normalizers['email_restorer'].restore(entity['email'])
            if email:
                entity['email'] = email
        
        # 添加大学和部门信息
        if university:
            entity['university'] = university
        if department:
            entity['department'] = department
        
        # 检查重复
        existing_entities = storage_manager.entity_storage.get_all()
        duplicate = normalizers['entity_deduplicator'].find_duplicate(entity, existing_entities)
        
        if duplicate:
            # 合并实体
            entity = normalizers['entity_deduplicator'].merge_entities(duplicate, entity)
            entity['id'] = duplicate.get('id')
            logger.debug(f"合并重复实体: {entity.get('name')}")
        else:
            # 生成新ID
            entity['id'] = normalizers['entity_deduplicator'].generate_entity_id(entity)
        
        # 保存实体
        if storage_manager.save_entity(entity):
            logger.info(f"保存实体: {entity.get('name')}")
        
        # 保存关系
        storage_manager.save_relations(entity)
        
        return True
        
    except Exception as e:
        logger.error(f"处理个人页任务失败: {url}, 错误: {e}", exc_info=True)
        return False


async def main_async():
    """异步主函数"""
    parser = argparse.ArgumentParser(
        description='教授信息爬取系统 - 从多个学校多个系爬取教授信息',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-c', '--config', type=str, default=None,
                       help='配置文件路径（默认: config.json）')
    
    args = parser.parse_args()
    
    # 初始化日志
    log_dir = Path(__file__).parent / "logs"
    logger = setup_logger("professor_crawler", str(log_dir))
    
    logger.info("=" * 60)
    logger.info("教授信息爬取系统")
    logger.info("=" * 60)
    
    # 加载配置
    logger.info("\n步骤 1: 加载配置")
    logger.info("-" * 60)
    
    config_path = Path(args.config) if args.config else Path(__file__).parent / "config.json"
    config = ConfigManager.load_config(config_path)
    
    logger.info(f"配置文件: {config_path}")
    
    # 清理输出目录（如果配置开启）
    clean_output_on_start = config.get('clean_output_on_start', False)
    if clean_output_on_start:
        logger.info("\n步骤 0: 清理输出目录")
        logger.info("-" * 60)
        data_dir = Path(__file__).parent / "data"
        clean_output_dir(str(data_dir), logger)
    
    # 初始化各个模块
    logger.info("\n步骤 2: 初始化各个模块")
    logger.info("-" * 60)
    
    # Discovery
    seed_manager = SeedManager(config, logger)
    
    # Scheduler
    retry_strategy = RetryStrategy(
        max_retries=config.get('scheduler', {}).get('retry_times', 3),
        base_delay=config.get('scheduler', {}).get('retry_delay', 5),
        logger=logger
    )
    task_manager = TaskManager(
        retry_strategy=retry_strategy,
        logger=logger,
        max_concurrent=config.get('scheduler', {}).get('max_concurrent_departments', 3)
    )
    
    # 延迟创建浏览器管理器的函数（只在需要动态抓取时调用）
    def get_or_create_browser_manager():
        """延迟创建浏览器管理器（只在需要动态抓取时调用）"""
        logger.info("\n检测到需要动态抓取，创建浏览器管理器")
        logger.info("-" * 60)
        
        browser_manager = None
        try:
            browser_manager = ChromeManager(config)
            logger.info("✅ 使用 Chrome 浏览器管理器")
        except Exception as e:
            try:
                browser_manager = EdgeManager(config)
                logger.info("✅ 使用 Edge 浏览器管理器")
            except Exception as e2:
                logger.error(f"❌ 无法创建浏览器管理器: {e}, {e2}")
                return None
        
        # 确保浏览器正在运行
        if not browser_manager.is_running():
            logger.warning("⚠️  浏览器未运行，尝试启动...")
            try:
                browser_manager.start()
                logger.info("✅ 浏览器已启动")
            except Exception as e:
                logger.error(f"❌ 启动浏览器失败: {e}")
                return None
        else:
            logger.info("✅ 浏览器已在运行")
        
        return browser_manager
    
    # Fetcher - 延迟创建浏览器管理器（只在需要动态抓取时才创建）
    # 先不创建浏览器管理器，让FetcherFactory在需要时才创建
    fetcher_factory = FetcherFactory(
        browser_manager=None,  # 延迟创建，不立即传入
        prefer_static=config.get('fetcher', {}).get('prefer_static', True),
        config=config.get('fetcher', {}),
        logger=logger,
        browser_manager_factory=get_or_create_browser_manager  # 传入工厂函数
    )
    
    # Parser
    parser_factory = ParserFactory(
        config=config.get('parser', {}),
        logger=logger
    )
    
    # Storage
    storage_manager = StorageManager(
        base_dir="data",
        config=config,
        logger=logger
    )
    
    # Normalization
    normalizers = {
        'field_normalizer': FieldNormalizer(logger),
        'name_parser': NameParser(logger),
        'email_restorer': EmailRestorer(logger),
        'entity_deduplicator': EntityDeduplicator(logger),
        'department_mapper': DepartmentMapper(logger)
    }
    
    # Update
    incremental_updater = IncrementalUpdater(
        config=config,
        raw_storage=storage_manager.raw_storage,
        logger=logger
    )
    version_manager = VersionManager(logger=logger)
    
    # 注册任务处理器
    async def list_page_handler(task):
        return await process_list_page_task(
            task, fetcher_factory, parser_factory, storage_manager,
            normalizers, incremental_updater, version_manager, logger
        )
    
    async def profile_page_handler(task):
        return await process_profile_page_task(
            task, fetcher_factory, parser_factory, storage_manager,
            normalizers, incremental_updater, version_manager, logger
        )
    
    task_manager.register_handler(TaskType.LIST_PAGE, list_page_handler)
    task_manager.register_handler(TaskType.PROFILE_PAGE, profile_page_handler)
    
    # 发现任务
    logger.info("\n步骤 5: 发现faculty页面URL")
    logger.info("-" * 60)
    
    tasks = seed_manager.discover_all()
    logger.info(f"发现 {len(tasks)} 个faculty页面URL")
    
    # 添加任务到队列
    for task_info in tasks:
        task_manager.add_task(
            task_type=task_info['task_type'],
            url=task_info['url'],
            priority=task_info['priority'],
            metadata=task_info['metadata']
        )
    
    # 运行任务管理器
    logger.info("\n步骤 6: 开始执行爬取任务")
    logger.info("-" * 60)
    
    await task_manager.run()
    
    # 打印统计信息
    logger.info("\n" + "=" * 60)
    logger.info("✅ 所有操作完成")
    logger.info("=" * 60)
    
    stats = storage_manager.get_stats()
    logger.info(f"实体数量: {stats['entities_count']}")
    logger.info(f"教授-部门关系: {stats['professor_department_relations']}")
    logger.info(f"教授-发表关系: {stats['professor_publication_relations']}")
    logger.info(f"教授-实验室关系: {stats['professor_lab_relations']}")
    
    task_stats = task_manager.get_stats()
    logger.info(f"总任务数: {task_stats['total']}")
    logger.info(f"已完成: {task_stats['completed']}")
    logger.info(f"失败: {task_stats['failed']}")
    logger.info(f"重试: {task_stats['retried']}")


def main():
    """主函数"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
