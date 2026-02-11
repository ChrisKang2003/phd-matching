"""
存储管理器
统一管理所有存储层
"""
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from storage.raw_storage import RawStorage
from storage.entity_storage import EntityStorage
from storage.relation_storage import RelationStorage
from fetcher.static_fetcher import FetchResult


class StorageManager:
    """存储管理器 - 统一管理所有存储层"""
    
    def __init__(
        self,
        base_dir: str = "data",
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化存储管理器
        
        Args:
            base_dir: 基础存储目录
            config: 配置字典
            logger: 日志记录器
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger("storage_manager")
        
        storage_config = self.config.get('storage', {})
        
        # 初始化各存储层
        self.raw_storage = RawStorage(
            base_dir=f"{base_dir}/raw_pages",
            save_html=storage_config.get('save_raw_html', True),
            logger=self.logger
        )
        
        self.entity_storage = EntityStorage(
            base_dir=f"{base_dir}/entities",
            logger=self.logger
        )
        
        self.relation_storage = RelationStorage(
            base_dir=f"{base_dir}/relations",
            logger=self.logger
        )
    
    def save_raw(
        self,
        fetch_result: FetchResult,
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        保存原始页面
        
        Args:
            fetch_result: 抓取结果
            university: 大学名称
            department: 系名称
            
        Returns:
            Dict[str, Any]: 保存信息
        """
        return self.raw_storage.save(fetch_result, university, department)
    
    def save_entity(self, entity: Dict[str, Any]) -> bool:
        """
        保存实体
        
        Args:
            entity: 实体数据
            
        Returns:
            bool: 是否保存成功
        """
        return self.entity_storage.save(entity)
    
    def save_relations(self, entity: Dict[str, Any]) -> bool:
        """
        保存实体关系
        
        Args:
            entity: 实体数据（包含关系信息）
            
        Returns:
            bool: 是否保存成功
        """
        entity_id = entity.get('id')
        if not entity_id:
            self.logger.warning("实体没有ID，无法保存关系")
            return False
        
        success = True
        
        # 保存教授-部门关系
        if 'department' in entity and 'university' in entity:
            success &= self.relation_storage.save_professor_department(
                entity_id,
                entity['department'],
                entity['university'],
                entity.get('role')
            )
        
        # 保存教授-实验室关系
        if 'lab' in entity:
            lab_info = entity['lab']
            if isinstance(lab_info, dict):
                success &= self.relation_storage.save_professor_lab(
                    entity_id,
                    lab_info.get('name', ''),
                    lab_info.get('url')
                )
            elif isinstance(lab_info, str):
                success &= self.relation_storage.save_professor_lab(
                    entity_id,
                    lab_info
                )
        
        # 保存教授-发表关系
        if 'publications' in entity:
            for publication in entity['publications']:
                success &= self.relation_storage.save_professor_publication(
                    entity_id,
                    publication
                )
        
        return success
    
    def get_latest_raw(self, url: str, university: Optional[str] = None, department: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取URL的最新原始版本
        
        Args:
            url: 页面URL
            university: 大学名称
            department: 系名称
            
        Returns:
            Optional[Dict[str, Any]]: 最新版本的元数据
        """
        return self.raw_storage.get_latest(url, university, department)
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            Optional[Dict[str, Any]]: 实体数据
        """
        return self.entity_storage.get(entity_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            'entities_count': self.entity_storage.count(),
            'professor_department_relations': len(self.relation_storage._professor_department),
            'professor_publication_relations': len(self.relation_storage._professor_publication),
            'professor_lab_relations': len(self.relation_storage._professor_lab)
        }

