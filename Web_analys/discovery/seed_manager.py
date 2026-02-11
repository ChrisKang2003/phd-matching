"""
种子源管理
从配置文件中读取学校、系、URL列表
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from Web_analys.scheduler import TaskType, TaskPriority


class SeedManager:
    """种子源管理器 - 手动维护的URL列表"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化种子源管理器
        
        Args:
            config: 配置字典（包含universities配置）
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger or logging.getLogger("seed_manager")
        self.universities = config.get('universities', [])
    
    def discover_all(self) -> List[Dict[str, Any]]:
        """
        发现所有faculty页面URL
        
        Returns:
            List[Dict[str, Any]]: URL任务列表（带标签）
        """
        tasks = []
        
        for university in self.universities:
            if not university.get('discovery', {}).get('enabled', True):
                self.logger.debug(f"跳过已禁用的大学: {university.get('name')}")
                continue
            
            university_tasks = self.discover_university(university)
            tasks.extend(university_tasks)
        
        self.logger.info(f"从种子源发现 {len(tasks)} 个faculty页面URL")
        return tasks
    
    def discover_university(self, university: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        发现单个大学的所有faculty页面URL
        
        Args:
            university: 大学配置
            
        Returns:
            List[Dict[str, Any]]: URL任务列表
        """
        tasks = []
        university_name = university.get('name', '')
        university_code = university.get('code', '')
        departments = university.get('departments', [])
        
        self.logger.info(f"发现大学: {university_name}")
        
        for department in departments:
            if not department.get('enabled', True):
                self.logger.debug(f"跳过已禁用的系: {department.get('name')}")
                continue
            
            department_tasks = self.discover_department(
                university_name,
                university_code,
                department
            )
            tasks.extend(department_tasks)
        
        return tasks
    
    def discover_department(
        self,
        university_name: str,
        university_code: str,
        department: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        发现单个系的faculty页面URL
        
        Args:
            university_name: 大学名称
            university_code: 大学代码
            department: 系配置
            
        Returns:
            List[Dict[str, Any]]: URL任务列表
        """
        tasks = []
        department_name = department.get('name', '')
        department_code = department.get('code', '')
        faculty_list_url = department.get('faculty_list_url', '')
        
        if not faculty_list_url:
            self.logger.warning(f"系没有配置faculty_list_url: {department_name}")
            return tasks
        
        # 创建列表页任务
        task = {
            'url': faculty_list_url,
            'task_type': TaskType.LIST_PAGE,
            'priority': TaskPriority.MEDIUM,
            'metadata': {
                'university': university_name,
                'university_code': university_code,
                'department': department_name,
                'department_code': department_code,
                'page_type': 'faculty_list',
                'adapter': department.get('adapter')  # 可选的站点适配器
            }
        }
        
        tasks.append(task)
        self.logger.debug(f"发现faculty列表页: {faculty_list_url} ({university_name} - {department_name})")
        
        return tasks
    
    def get_university_config(self, university_code: str) -> Optional[Dict[str, Any]]:
        """
        获取大学配置
        
        Args:
            university_code: 大学代码
            
        Returns:
            Optional[Dict[str, Any]]: 大学配置
        """
        for university in self.universities:
            if university.get('code') == university_code:
                return university
        return None
    
    def get_department_config(
        self,
        university_code: str,
        department_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取系配置
        
        Args:
            university_code: 大学代码
            department_code: 系代码
            
        Returns:
            Optional[Dict[str, Any]]: 系配置
        """
        university = self.get_university_config(university_code)
        if not university:
            return None
        
        for department in university.get('departments', []):
            if department.get('code') == department_code:
                return department
        
        return None

