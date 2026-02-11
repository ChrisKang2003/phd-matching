"""
实体消歧/合并
处理同一个人多个页面/多个部门兼职的情况
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class EntityDeduplicator:
    """实体消歧/合并器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化实体消歧器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("entity_deduplicator")
    
    def generate_entity_id(self, entity: Dict[str, Any]) -> str:
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
            try:
                domain = urlparse(homepage).netloc
                if domain:
                    safe_name = name.lower().replace(' ', '_')
                    return f"homepage_{domain}_{safe_name}"
            except Exception:
                pass
        
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
            safe_name = name.lower().replace(' ', '_')
            safe_dept = department.lower().replace(' ', '_')
            safe_uni = university.lower().replace(' ', '_')
            return f"name_{safe_name}_{safe_dept}_{safe_uni}"
        
        # 最后：使用时间戳（临时ID）
        import time
        return f"temp_{int(time.time())}"
    
    def find_duplicate(
        self,
        entity: Dict[str, Any],
        existing_entities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        查找重复实体
        
        改进逻辑：
        1. 如果新实体有email，优先用email匹配（即使现有实体没有email，如果姓名相同也合并）
        2. 如果新实体没有email，但现有实体有email且姓名相同，也合并
        3. 其他匹配逻辑保持不变
        
        Args:
            entity: 新实体
            existing_entities: 现有实体列表
            
        Returns:
            Optional[Dict[str, Any]]: 如果找到重复则返回现有实体，否则返回None
        """
        entity_name = entity.get('name', '').strip().lower()
        entity_email = entity.get('email', '').strip().lower()
        entity_department = entity.get('department', '').strip().lower()
        entity_university = entity.get('university', '').strip().lower()
        
        # 按优先级检查
        # 优先级1: email（精确匹配）
        if entity_email:
            for existing in existing_entities:
                existing_email = existing.get('email', '').strip().lower()
                if existing_email and existing_email == entity_email:
                    return existing
        
        # 优先级2: 姓名 + email（如果新实体有email，现有实体也有email，且姓名相同）
        if entity_email and entity_name:
            for existing in existing_entities:
                existing_email = existing.get('email', '').strip().lower()
                existing_name = existing.get('name', '').strip().lower()
                if existing_email and existing_name == entity_name:
                    # 即使email不同，如果姓名相同且在同一部门，也可能是同一人
                    existing_dept = existing.get('department', '').strip().lower()
                    existing_uni = existing.get('university', '').strip().lower()
                    if (existing_dept == entity_department and 
                        existing_uni == entity_university):
                        return existing
        
        # 优先级3: 姓名 + 部门 + 大学（即使email不同，如果姓名、部门、大学都相同，也合并）
        if entity_name and entity_department and entity_university:
            for existing in existing_entities:
                existing_name = existing.get('name', '').strip().lower()
                existing_dept = existing.get('department', '').strip().lower()
                existing_uni = existing.get('university', '').strip().lower()
                
                if (existing_name == entity_name and
                    existing_dept == entity_department and
                    existing_uni == entity_university):
                    return existing
        
        # 优先级4: homepage + name
        homepage = entity.get('homepage', '').strip()
        if homepage and entity_name:
            try:
                domain = urlparse(homepage).netloc
                if domain:
                    for existing in existing_entities:
                        existing_homepage = existing.get('homepage', '').strip()
                        existing_name = existing.get('name', '').strip().lower()
                        if existing_homepage and existing_name:
                            existing_domain = urlparse(existing_homepage).netloc
                            if existing_domain == domain and existing_name == entity_name:
                                return existing
            except Exception:
                pass
        
        # 优先级5: scholar_id / ORCID
        scholar_id = entity.get('google_scholar_id', '').strip()
        if scholar_id:
            for existing in existing_entities:
                if existing.get('google_scholar_id', '').strip() == scholar_id:
                    return existing
        
        orcid = entity.get('orcid', '').strip()
        if orcid:
            for existing in existing_entities:
                if existing.get('orcid', '').strip() == orcid:
                    return existing
        
        return None
    
    def merge_entities(
        self,
        entity1: Dict[str, Any],
        entity2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        合并两个实体
        
        Args:
            entity1: 实体1（通常是现有实体）
            entity2: 实体2（通常是新实体）
            
        Returns:
            Dict[str, Any]: 合并后的实体
        """
        merged = entity1.copy()
        
        # 合并字段（entity2的值优先，如果entity1没有）
        for key, value in entity2.items():
            if key not in merged or not merged[key]:
                merged[key] = value
            elif key == 'departments' and isinstance(merged[key], list):
                # 合并部门列表
                if isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key].append(value)
        
        # 标记为已合并
        merged['merged_from'] = [entity1.get('id'), entity2.get('id')]
        
        return merged

