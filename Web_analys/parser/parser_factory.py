"""
解析器工厂
根据页面特征选择合适的解析器
"""
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from parser.base_parser import BaseParser
from parser.general_parser import GeneralParser


class ParserFactory:
    """解析器工厂"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化解析器工厂
        
        Args:
            config: 配置字典
            logger: 日志记录器
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger("parser_factory")
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        # 创建通用解析器
        self.general_parser = GeneralParser(logger=self.logger)
        
        # 站点适配器映射（未来扩展）
        self.site_adapters: Dict[str, BaseParser] = {}
    
    def get_parser(self, url: str, html: str, adapter_name: Optional[str] = None) -> BaseParser:
        """
        获取合适的解析器
        
        Args:
            url: 页面URL
            html: HTML内容
            adapter_name: 站点适配器名称（如果指定）
            
        Returns:
            BaseParser: 解析器实例
        """
        # 如果指定了适配器，使用适配器
        if adapter_name and adapter_name in self.site_adapters:
            self.logger.debug(f"使用站点适配器: {adapter_name}")
            return self.site_adapters[adapter_name]
        
        # 否则使用通用解析器
        return self.general_parser
    
    def parse(self, html: str, url: str, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """
        解析HTML内容
        
        Args:
            html: HTML内容
            url: 页面URL
            adapter_name: 站点适配器名称（如果指定）
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        parser = self.get_parser(url, html, adapter_name)
        result = parser.parse(html, url)
        
        # 检查置信度
        confidence = result.get('confidence', 0.0)
        if confidence < self.confidence_threshold:
            self.logger.warning(
                f"解析置信度较低 ({confidence:.2f} < {self.confidence_threshold}): {url}"
            )
        
        return result
    
    def register_adapter(self, name: str, adapter: BaseParser):
        """
        注册站点适配器
        
        Args:
            name: 适配器名称
            adapter: 适配器实例
        """
        self.site_adapters[name] = adapter
        self.logger.info(f"注册站点适配器: {name}")

