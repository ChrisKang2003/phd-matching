"""
任务队列
管理不同类型的爬取任务
"""
import sys
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from queue import PriorityQueue

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class TaskType(Enum):
    """任务类型"""
    DISCOVER = "discover"  # 新学校发现任务
    LIST_PAGE = "list_page"  # 列表页更新任务
    PROFILE_PAGE = "profile_page"  # 个人页更新任务


class TaskPriority(Enum):
    """任务优先级（数字越小优先级越高）"""
    HIGH = 1  # 新学校discovery
    MEDIUM = 2  # 列表页更新
    LOW = 3  # 个人页更新


@dataclass
class Task:
    """爬取任务"""
    task_id: str
    task_type: TaskType
    url: str
    priority: TaskPriority = TaskPriority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """用于优先级队列排序"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self):
        """初始化任务队列"""
        self._queue = PriorityQueue()
        self._task_map: Dict[str, Task] = {}  # 用于快速查找任务
        self._completed_tasks: set = set()  # 已完成的任务ID
    
    def add_task(self, task: Task) -> bool:
        """
        添加任务到队列
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否添加成功
        """
        if task.task_id in self._task_map:
            return False  # 任务已存在
        
        self._queue.put(task)
        self._task_map[task.task_id] = task
        return True
    
    def get_task(self) -> Optional[Task]:
        """
        从队列获取下一个任务（按优先级）
        
        Returns:
            Optional[Task]: 任务对象，如果队列为空则返回None
        """
        if self._queue.empty():
            return None
        
        task = self._queue.get()
        
        # 如果任务已完成，跳过
        if task.task_id in self._completed_tasks:
            return self.get_task()  # 递归获取下一个
        
        return task
    
    def mark_complete(self, task_id: str) -> bool:
        """
        标记任务为已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否标记成功
        """
        if task_id in self._task_map:
            self._completed_tasks.add(task_id)
            return True
        return False
    
    def mark_failed(self, task_id: str) -> Optional[Task]:
        """
        标记任务为失败，如果未超过最大重试次数，则重新加入队列
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Task]: 如果重新加入队列则返回任务对象，否则返回None
        """
        if task_id not in self._task_map:
            return None
        
        task = self._task_map[task_id]
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # 重新加入队列
            self._queue.put(task)
            return task
        else:
            # 超过最大重试次数，标记为失败
            self._completed_tasks.add(task_id)
            return None
    
    def has_tasks(self) -> bool:
        """
        检查是否还有未完成的任务
        
        Returns:
            bool: 是否还有任务
        """
        return not self._queue.empty() or len(self._task_map) > len(self._completed_tasks)
    
    def get_queue_size(self) -> int:
        """
        获取队列大小
        
        Returns:
            int: 队列中的任务数量
        """
        return self._queue.qsize()
    
    def get_completed_count(self) -> int:
        """
        获取已完成任务数量
        
        Returns:
            int: 已完成任务数量
        """
        return len(self._completed_tasks)
    
    def clear(self):
        """清空队列"""
        while not self._queue.empty():
            self._queue.get()
        self._task_map.clear()
        self._completed_tasks.clear()

