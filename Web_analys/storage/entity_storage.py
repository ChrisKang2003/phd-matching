"""
实体存储
存储归一化后的教授实体
"""
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class EntityStorage:
    """实体存储 - 存储归一化后的教授实体"""
    
    def __init__(
        self,
        base_dir: str = "data/entities",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化实体存储
        
        Args:
            base_dir: 基础存储目录
            logger: 日志记录器
        """
        self.base_dir = Path(base_dir)
        self.logger = logger or logging.getLogger("entity_storage")
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 实体文件路径
        self.professors_file = self.base_dir / "professors.json"
        
        # 加载现有实体
        self._entities: Dict[str, Dict[str, Any]] = self._load_entities()
    
    def save(self, entity: Dict[str, Any]) -> bool:
        """
        保存实体
        
        Args:
            entity: 实体数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 生成实体ID
            entity_id = self._generate_entity_id(entity)
            
            # 添加/更新实体
            entity['id'] = entity_id
            entity['updated_at'] = datetime.now().isoformat()
            
            if entity_id not in self._entities:
                entity['created_at'] = datetime.now().isoformat()
            
            self._entities[entity_id] = entity
            
            # 保存到文件
            self._save_entities()
            
            self.logger.debug(f"保存实体: {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存实体失败: {e}", exc_info=True)
            return False
    
    def save_batch(self, entities: List[Dict[str, Any]]) -> int:
        """
        批量保存实体
        
        Args:
            entities: 实体列表
            
        Returns:
            int: 成功保存的数量
        """
        count = 0
        for entity in entities:
            if self.save(entity):
                count += 1
        
        self.logger.info(f"批量保存实体: {count}/{len(entities)}")
        return count
    
    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            Optional[Dict[str, Any]]: 实体数据
        """
        return self._entities.get(entity_id)
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        根据邮箱查找实体
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[Dict[str, Any]]: 实体数据
        """
        for entity in self._entities.values():
            if entity.get('email', '').lower() == email.lower():
                return entity
        return None
    
    def find_by_name(self, name: str, university: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        根据姓名查找实体
        
        Args:
            name: 姓名
            university: 大学名称（可选）
            
        Returns:
            List[Dict[str, Any]]: 实体列表
        """
        results = []
        name_lower = name.lower()
        
        for entity in self._entities.values():
            entity_name = entity.get('name', '').lower()
            if name_lower in entity_name or entity_name in name_lower:
                if not university or entity.get('university') == university:
                    results.append(entity)
        
        return results
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有实体
        
        Returns:
            List[Dict[str, Any]]: 实体列表
        """
        return list(self._entities.values())
    
    def count(self) -> int:
        """
        获取实体数量
        
        Returns:
            int: 实体数量
        """
        return len(self._entities)
    
    def _generate_entity_id(self, entity: Dict[str, Any]) -> str:
        """
        生成实体ID（基于主键优先级）
        
        优先级：(email) > (homepage+name) > (scholar_id/ORCID) > (name+dept+uni)
        
        Args:
            entity: 实体数据
            
        Returns:
            str: 实体ID
        """
        # 优先级1: email
        email = entity.get('email', '').strip()
        if email:
            return f"email_{email.lower()}"
        
        # 优先级2: homepage + name
        homepage = entity.get('homepage', '').strip()
        name = entity.get('name', '').strip()
        if homepage and name:
            from urllib.parse import urlparse
            domain = urlparse(homepage).netloc
            return f"homepage_{domain}_{name.lower().replace(' ', '_')}"
        
        # 优先级3: scholar_id / ORCID
        scholar_id = entity.get('google_scholar_id', '').strip()
        if scholar_id:
            return f"scholar_{scholar_id}"
        
        orcid = entity.get('orcid', '').strip()
        if orcid:
            return f"orcid_{orcid}"
        
        # 优先级4: name + department + university
        department = entity.get('department', '').strip()
        university = entity.get('university', '').strip()
        if name and department and university:
            return f"name_{name.lower().replace(' ', '_')}_{department.lower().replace(' ', '_')}_{university.lower().replace(' ', '_')}"
        
        # 最后：使用时间戳
        return f"temp_{datetime.now().timestamp()}"
    
    def _load_entities(self) -> Dict[str, Dict[str, Any]]:
        """
        从文件加载实体
        
        Returns:
            Dict[str, Dict[str, Any]]: 实体字典
        """
        if not self.professors_file.exists():
            return {}
        
        try:
            with open(self.professors_file, 'r', encoding='utf-8') as f:
                entities_list = json.load(f)
                return {entity['id']: entity for entity in entities_list if 'id' in entity}
        except Exception as e:
            self.logger.error(f"加载实体失败: {e}", exc_info=True)
            return {}
    
    def _save_entities(self):
        """保存实体到文件"""
        try:
            entities_list = list(self._entities.values())
            with open(self.professors_file, 'w', encoding='utf-8') as f:
                json.dump(entities_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存实体失败: {e}", exc_info=True)

