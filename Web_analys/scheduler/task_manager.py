"""
任务管理器
负责任务调度和执行
"""
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from scheduler.task_queue import TaskQueue, Task, TaskType, TaskPriority
from scheduler.retry_strategy import RetryStrategy


class TaskManager:
    """任务管理器"""
    
    def __init__(
        self,
        retry_strategy: Optional[RetryStrategy] = None,
        logger: Optional[logging.Logger] = None,
        max_concurrent: int = 3
    ):
        """
        初始化任务管理器
        
        Args:
            retry_strategy: 重试策略
            logger: 日志记录器
            max_concurrent: 最大并发任务数
        """
        self.task_queue = TaskQueue()
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.logger = logger or logging.getLogger("task_manager")
        self.max_concurrent = max_concurrent
        self._task_handlers: Dict[TaskType, Callable] = {}
        self._running_tasks: set = set()  # 正在运行的任务ID
        self._stats = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "retried": 0
        }
    
    def register_handler(self, task_type: TaskType, handler: Callable):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理函数（异步）
        """
        self._task_handlers[task_type] = handler
        self.logger.info(f"✅ 注册任务处理器: {task_type.value} ({task_type})")
    
    def add_task(
        self,
        task_type: TaskType,
        url: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> str:
        """
        添加任务到队列
        
        Args:
            task_type: 任务类型
            url: 任务URL
            priority: 任务优先级
            metadata: 任务元数据
            max_retries: 最大重试次数
            
        Returns:
            str: 任务ID
        """
        task_id = f"{task_type.value}_{url}_{datetime.now().timestamp()}"
        task = Task(
            task_id=task_id,
            task_type=task_type,
            url=url,
            priority=priority,
            metadata=metadata or {},
            max_retries=max_retries
        )
        
        if self.task_queue.add_task(task):
            self._stats["total"] += 1
            self.logger.info(f"添加任务: {task_id} ({task_type.value})")
            return task_id
        else:
            self.logger.warning(f"任务已存在，未添加: {task_id}")
            return task_id
    
    async def execute_task(self, task: Task) -> bool:
        """
        执行单个任务
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否执行成功
        """
        task_type = task.task_type
        
        if task_type not in self._task_handlers:
            self.logger.error(f"未找到任务处理器: {task_type.value} ({task_type})")
            self.logger.error(f"已注册的处理器: {[t.value for t in self._task_handlers.keys()]}")
            return False
        
        handler = self._task_handlers[task_type]
        self._running_tasks.add(task.task_id)
        
        try:
            self.logger.info(f"开始执行任务: {task.task_id} ({task.url})")
            result = await handler(task)
            
            if result:
                self.task_queue.mark_complete(task.task_id)
                self._stats["completed"] += 1
                self.logger.info(f"任务完成: {task.task_id}")
                return True
            else:
                self.logger.warning(f"任务执行失败: {task.task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"任务执行异常: {task.task_id}, 错误: {e}", exc_info=True)
            return False
            
        finally:
            self._running_tasks.discard(task.task_id)
    
    async def process_next_task(self) -> bool:
        """
        处理下一个任务
        
        Returns:
            bool: 是否处理了任务
        """
        # 检查并发限制
        if len(self._running_tasks) >= self.max_concurrent:
            return False
        
        task = self.task_queue.get_task()
        if task is None:
            return False
        
        # 检查是否应该重试
        if not self.retry_strategy.should_retry(task.retry_count, task.url):
            self.task_queue.mark_complete(task.task_id)
            self._stats["failed"] += 1
            self.logger.warning(f"任务超过最大重试次数或已黑名单: {task.task_id}")
            return False
        
        # 如果需要重试，等待
        if task.retry_count > 0:
            await self.retry_strategy.wait_before_retry(task.retry_count)
            self._stats["retried"] += 1
        
        # 执行任务
        success = await self.execute_task(task)
        
        if not success:
            # 任务失败，尝试重新加入队列
            retry_task = self.task_queue.mark_failed(task.task_id)
            if retry_task:
                self.logger.info(f"任务将重试: {task.task_id} (第 {retry_task.retry_count} 次)")
            else:
                self._stats["failed"] += 1
                self.logger.error(f"任务最终失败: {task.task_id}")
        
        return True
    
    async def run(self, stop_condition: Optional[Callable[[], bool]] = None):
        """
        运行任务管理器（持续处理任务）
        
        Args:
            stop_condition: 停止条件函数（返回True时停止）
        """
        self.logger.info("任务管理器开始运行")
        
        while True:
            # 检查停止条件
            if stop_condition and stop_condition():
                self.logger.info("满足停止条件，任务管理器停止")
                break
            
            # 检查是否还有任务
            if not self.task_queue.has_tasks() and len(self._running_tasks) == 0:
                self.logger.info("所有任务已完成，任务管理器停止")
                break
            
            # 处理任务
            processed = await self.process_next_task()
            
            if not processed:
                # 没有处理任务，等待一下
                await asyncio.sleep(0.1)
        
        self.logger.info("任务管理器已停止")
        self._print_stats()
    
    def _print_stats(self):
        """打印统计信息"""
        self.logger.info("=" * 60)
        self.logger.info("任务统计:")
        self.logger.info(f"  总任务数: {self._stats['total']}")
        self.logger.info(f"  已完成: {self._stats['completed']}")
        self.logger.info(f"  失败: {self._stats['failed']}")
        self.logger.info(f"  重试: {self._stats['retried']}")
        self.logger.info("=" * 60)
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        return self._stats.copy()
    
    def has_tasks(self) -> bool:
        """
        检查是否还有任务
        
        Returns:
            bool: 是否还有任务
        """
        return self.task_queue.has_tasks() or len(self._running_tasks) > 0

