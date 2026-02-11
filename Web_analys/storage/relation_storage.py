"""
关系存储
存储实体之间的关系（professor-department, professor-publication等）
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


class RelationStorage:
    """关系存储 - 存储实体之间的关系"""
    
    def __init__(
        self,
        base_dir: str = "data/relations",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化关系存储
        
        Args:
            base_dir: 基础存储目录
            logger: 日志记录器
        """
        self.base_dir = Path(base_dir)
        self.logger = logger or logging.getLogger("relation_storage")
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 关系文件路径
        self.professor_department_file = self.base_dir / "professor_department.json"
        self.professor_publication_file = self.base_dir / "professor_publication.json"
        self.professor_lab_file = self.base_dir / "professor_lab.json"
        
        # 加载现有关系
        self._professor_department: List[Dict[str, Any]] = self._load_relations(self.professor_department_file)
        self._professor_publication: List[Dict[str, Any]] = self._load_relations(self.professor_publication_file)
        self._professor_lab: List[Dict[str, Any]] = self._load_relations(self.professor_lab_file)
    
    def save_professor_department(
        self,
        professor_id: str,
        department: str,
        university: str,
        role: Optional[str] = None
    ) -> bool:
        """
        保存教授-部门关系
        
        Args:
            professor_id: 教授实体ID
            department: 部门名称
            university: 大学名称
            role: 角色（如：primary, secondary）
            
        Returns:
            bool: 是否保存成功
        """
        relation = {
            'professor_id': professor_id,
            'department': department,
            'university': university,
            'role': role or 'primary',
            'created_at': datetime.now().isoformat()
        }
        
        # 检查是否已存在
        if not self._relation_exists(self._professor_department, relation):
            self._professor_department.append(relation)
            self._save_relations(self.professor_department_file, self._professor_department)
            self.logger.debug(f"保存教授-部门关系: {professor_id} -> {department}")
            return True
        
        return False
    
    def save_professor_publication(
        self,
        professor_id: str,
        publication: Dict[str, Any]
    ) -> bool:
        """
        保存教授-发表关系
        
        Args:
            professor_id: 教授实体ID
            publication: 发表信息
            
        Returns:
            bool: 是否保存成功
        """
        relation = {
            'professor_id': professor_id,
            'publication': publication,
            'created_at': datetime.now().isoformat()
        }
        
        # 检查是否已存在（基于标题和年份）
        if not self._publication_exists(self._professor_publication, relation):
            self._professor_publication.append(relation)
            self._save_relations(self.professor_publication_file, self._professor_publication)
            self.logger.debug(f"保存教授-发表关系: {professor_id}")
            return True
        
        return False
    
    def save_professor_lab(
        self,
        professor_id: str,
        lab_name: str,
        lab_url: Optional[str] = None
    ) -> bool:
        """
        保存教授-实验室关系
        
        Args:
            professor_id: 教授实体ID
            lab_name: 实验室名称
            lab_url: 实验室URL（可选）
            
        Returns:
            bool: 是否保存成功
        """
        relation = {
            'professor_id': professor_id,
            'lab_name': lab_name,
            'lab_url': lab_url,
            'created_at': datetime.now().isoformat()
        }
        
        if not self._relation_exists(self._professor_lab, relation):
            self._professor_lab.append(relation)
            self._save_relations(self.professor_lab_file, self._professor_lab)
            self.logger.debug(f"保存教授-实验室关系: {professor_id} -> {lab_name}")
            return True
        
        return False
    
    def get_professor_departments(self, professor_id: str) -> List[Dict[str, Any]]:
        """
        获取教授的所有部门
        
        Args:
            professor_id: 教授实体ID
            
        Returns:
            List[Dict[str, Any]]: 部门关系列表
        """
        return [
            rel for rel in self._professor_department
            if rel['professor_id'] == professor_id
        ]
    
    def get_professor_publications(self, professor_id: str) -> List[Dict[str, Any]]:
        """
        获取教授的所有发表
        
        Args:
            professor_id: 教授实体ID
            
        Returns:
            List[Dict[str, Any]]: 发表关系列表
        """
        return [
            rel for rel in self._professor_publication
            if rel['professor_id'] == professor_id
        ]
    
    def _relation_exists(self, relations: List[Dict[str, Any]], new_relation: Dict[str, Any]) -> bool:
        """检查关系是否已存在"""
        for rel in relations:
            if (rel.get('professor_id') == new_relation.get('professor_id') and
                rel.get('department') == new_relation.get('department') and
                rel.get('university') == new_relation.get('university')):
                return True
        return False
    
    def _publication_exists(self, relations: List[Dict[str, Any]], new_relation: Dict[str, Any]) -> bool:
        """检查发表是否已存在"""
        new_pub = new_relation.get('publication', {})
        for rel in relations:
            if rel.get('professor_id') == new_relation.get('professor_id'):
                pub = rel.get('publication', {})
                if (pub.get('title') == new_pub.get('title') and
                    pub.get('year') == new_pub.get('year')):
                    return True
        return False
    
    def _load_relations(self, file_path: Path) -> List[Dict[str, Any]]:
        """从文件加载关系"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载关系失败: {file_path}, 错误: {e}", exc_info=True)
            return []
    
    def _save_relations(self, file_path: Path, relations: List[Dict[str, Any]]):
        """保存关系到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(relations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存关系失败: {file_path}, 错误: {e}", exc_info=True)

