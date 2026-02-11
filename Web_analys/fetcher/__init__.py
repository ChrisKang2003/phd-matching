"""
抓取器模块
负责获取网页内容（静态或动态）
"""
from .static_fetcher import StaticFetcher
from .dynamic_fetcher import DynamicFetcher
from .fetcher_factory import FetcherFactory

__all__ = ['StaticFetcher', 'DynamicFetcher', 'FetcherFactory']

