"""
增量更新
管理列表页和个人页的更新频率
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from update.change_detector import ChangeDetector
from storage.raw_storage import RawStorage


class IncrementalUpdater:
    """增量更新器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        raw_storage: RawStorage,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化增量更新器
        
        Args:
            config: 配置字典
            raw_storage: 原始存储
            logger: 日志记录器
        """
        self.config = config
        self.raw_storage = raw_storage
        self.logger = logger or logging.getLogger("incremental_updater")
        
        update_config = config.get('update', {})
        self.list_page_interval = timedelta(days=update_config.get('list_page_interval_days', 14))
        self.profile_page_interval = timedelta(days=update_config.get('profile_page_interval_days', 60))
        self.enable_change_detection = update_config.get('enable_change_detection', True)
        self.force_update = update_config.get('force_update', False)  # 强制更新，忽略时间间隔
        
        self.change_detector = ChangeDetector(logger=self.logger) if self.enable_change_detection else None
    
    def should_update(
        self,
        url: str,
        page_type: str,
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> bool:
        """
        判断是否应该更新页面
        
        Args:
            url: 页面URL
            page_type: 页面类型（'faculty_list' 或 'profile'）
            university: 大学名称
            department: 系名称
            
        Returns:
            bool: 是否应该更新
        """
        # 如果强制更新，直接返回True
        if self.force_update:
            self.logger.info(f"✅ 强制更新模式，总是更新: {url}")
            return True
        
        # 获取最新版本
        latest = self.raw_storage.get_latest(url, university, department)
        
        if not latest:
            # 没有历史记录，需要抓取
            self.logger.info(f"✅ 没有历史记录，需要抓取: {url}")
            return True
        
        # 检查更新时间
        fetched_at_str = latest.get('fetched_at')
        if not fetched_at_str:
            self.logger.info(f"✅ 没有fetched_at时间，需要更新: {url}")
            return True
        
        try:
            fetched_at = datetime.fromisoformat(fetched_at_str)
            now = datetime.now()
            elapsed = now - fetched_at
            
            # 根据页面类型选择更新间隔
            if page_type == 'faculty_list':
                interval = self.list_page_interval
            elif page_type == 'profile':
                interval = self.profile_page_interval
            else:
                interval = self.list_page_interval  # 默认使用列表页间隔
            
            self.logger.info(f"⏰ 时间检查 - 上次抓取: {fetched_at_str}, "
                           f"已过: {elapsed.days} 天 {elapsed.seconds//3600} 小时, "
                           f"需要间隔: {interval.days} 天")
            
            if elapsed >= interval:
                self.logger.info(f"✅ 超过更新间隔，需要更新: {url} (已过 {elapsed.days} 天)")
                return True
            else:
                remaining_days = interval.days - elapsed.days
                self.logger.warning(f"⏸️  未超过更新间隔，跳过: {url} (还有 {remaining_days} 天)")
                return False
                
        except Exception as e:
            self.logger.warning(f"⚠️  解析更新时间失败: {url}, 错误: {e}，默认更新")
            return True
    
    def is_changed(
        self,
        current_html: str,
        url: str,
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> bool:
        """
        检测内容是否发生变化
        
        Args:
            current_html: 当前HTML内容
            url: 页面URL
            university: 大学名称
            department: 系名称
            
        Returns:
            bool: 是否发生变化
        """
        if not self.enable_change_detection or not self.change_detector:
            self.logger.info(f"✅ 变更检测已禁用，认为内容已变化: {url}")
            return True  # 如果未启用变更检测，默认认为已变化
        
        # 获取最新版本的hash
        latest = self.raw_storage.get_latest(url, university, department)
        if not latest:
            self.logger.info(f"✅ 没有历史记录，认为内容已变化: {url}")
            return True  # 没有历史记录，认为已变化
        
        previous_hash = latest.get('hash', '')
        if not previous_hash:
            self.logger.info(f"✅ 没有历史hash，认为内容已变化: {url}")
            return True  # 没有hash，认为已变化
        
        # 计算当前内容的hash
        from utils.hash_utils import calculate_content_hash
        current_hash = calculate_content_hash(current_html)
        
        is_changed = self.change_detector.is_changed(current_html, previous_hash)
        self.logger.info(f"🔍 Hash比较 - 上次: {previous_hash[:16]}..., "
                        f"当前: {current_hash[:16]}..., "
                        f"是否变化: {is_changed}")
        
        return is_changed

