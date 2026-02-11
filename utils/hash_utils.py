"""
Hash工具函数
用于内容变更检测
"""
import hashlib
from typing import Optional
from bs4 import BeautifulSoup


def calculate_content_hash(html: str, exclude_tags: Optional[list] = None) -> str:
    """
    计算HTML内容的hash值（排除指定标签）
    
    Args:
        html: HTML内容
        exclude_tags: 要排除的标签列表（如时间、脚注、导航等）
        
    Returns:
        str: 内容的hash值
    """
    if exclude_tags is None:
        exclude_tags = ['time', 'footer', 'nav', 'script', 'style', 'meta']
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除排除的标签
        for tag in exclude_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # 获取文本内容
        text_content = soup.get_text(separator=' ', strip=True)
        
        # 计算hash
        hash_obj = hashlib.sha256(text_content.encode('utf-8'))
        return hash_obj.hexdigest()
        
    except Exception:
        # 如果解析失败，直接对原始HTML计算hash
        hash_obj = hashlib.sha256(html.encode('utf-8'))
        return hash_obj.hexdigest()


def calculate_file_hash(file_path: str) -> str:
    """
    计算文件的hash值
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件的hash值
    """
    hash_obj = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return ""

