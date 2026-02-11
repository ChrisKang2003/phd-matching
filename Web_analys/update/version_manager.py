"""
版本管理
保存raw_html + parsed_json + fetched_at，用于回溯和纠错
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))


class VersionManager:
    """版本管理器"""
    
    def __init__(
        self,
        base_dir: str = "data/versions",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化版本管理器
        
        Args:
            base_dir: 基础存储目录
            logger: 日志记录器
        """
        self.base_dir = Path(base_dir)
        self.logger = logger or logging.getLogger("version_manager")
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_version(
        self,
        url: str,
        html: str,
        parsed_json: Dict[str, Any],
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> str:
        """
        保存版本（raw_html + parsed_json + fetched_at）
        
        Args:
            url: 页面URL
            html: HTML内容
            parsed_json: 解析后的JSON数据
            university: 大学名称
            department: 系名称
            
        Returns:
            str: 版本文件路径
        """
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        
        # 生成存储路径
        if university and department:
            safe_university = self._sanitize_filename(university)
            safe_department = self._sanitize_filename(department)
            version_dir = self.base_dir / safe_university / safe_department
        else:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            version_dir = self.base_dir / self._sanitize_filename(domain)
        
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存版本数据
        version_data = {
            'url': url,
            'fetched_at': timestamp.isoformat(),
            'html': html,
            'parsed_json': parsed_json,
            'university': university,
            'department': department
        }
        
        version_file = version_dir / f"{timestamp_str}_version.json"
        
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"保存版本: {version_file}")
            return str(version_file)
            
        except Exception as e:
            self.logger.error(f"保存版本失败: {version_file}, 错误: {e}", exc_info=True)
            return ""
    
    def load_version(self, version_file: str) -> Optional[Dict[str, Any]]:
        """
        加载版本数据
        
        Args:
            version_file: 版本文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 版本数据
        """
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载版本失败: {version_file}, 错误: {e}", exc_info=True)
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        import re
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        if len(safe) > 100:
            safe = safe[:100]
        return safe.rstrip('_')

