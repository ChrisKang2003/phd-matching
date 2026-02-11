"""
原始页面存储
存储raw_pages（url, html, status, headers, fetched_at, hash）
"""
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加 utils 目录到路径
utils_path = Path(__file__).parent.parent.parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

try:
    from utils.hash_utils import calculate_content_hash
except ImportError:
    # 如果直接导入失败，尝试相对导入
    import sys
    from pathlib import Path
    utils_path = Path(__file__).parent.parent.parent / "utils"
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    from hash_utils import calculate_content_hash
from fetcher.static_fetcher import FetchResult


class RawStorage:
    """原始页面存储"""
    
    def __init__(
        self,
        base_dir: str = "data/raw_pages",
        save_html: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化原始存储
        
        Args:
            base_dir: 基础存储目录
            save_html: 是否保存HTML文件
            logger: 日志记录器
        """
        self.base_dir = Path(base_dir)
        self.save_html = save_html
        self.logger = logger or logging.getLogger("raw_storage")
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(
        self,
        fetch_result: FetchResult,
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        保存原始页面
        
        Args:
            fetch_result: 抓取结果
            university: 大学名称
            department: 系名称
            metadata: 额外元数据
            
        Returns:
            Dict[str, Any]: 保存信息（包含文件路径、hash等）
        """
        if not fetch_result.success:
            self.logger.warning(f"抓取失败，不保存: {fetch_result.url}")
            return {}
        
        # 生成存储路径
        storage_path = self._generate_storage_path(
            fetch_result.url,
            university,
            department
        )
        
        # 计算内容hash
        content_hash = calculate_content_hash(fetch_result.html)
        
        # 保存HTML文件（使用固定文件名，新文件会覆盖旧文件）
        html_path = None
        if self.save_html:
            html_path = storage_path / "page.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果文件已存在，记录覆盖信息
            file_existed = html_path.exists()
            if file_existed:
                old_size = html_path.stat().st_size if html_path.exists() else 0
                self.logger.info(f"📝 文件已存在，将覆盖: {html_path} (旧文件大小: {old_size} 字节)")
            else:
                self.logger.info(f"📝 创建新文件: {html_path}")
            
            # 调试：检查要保存的内容
            html_content = fetch_result.html
            self.logger.info(f"💾 准备保存HTML - 长度: {len(html_content)} 字符")
            self.logger.info(f"   前100字符: {repr(html_content[:100])}")
            is_valid = html_content.strip()[:50].lower().startswith(('<!', '<html'))
            self.logger.info(f"   是有效HTML: {is_valid}")
            
            # 保存文件
            try:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"✅ HTML文件写入成功: {html_path}")
            except Exception as e:
                self.logger.error(f"❌ HTML文件写入失败: {html_path}, 错误: {e}")
                raise
            
            # 验证保存后的文件
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read(100)
                new_size = html_path.stat().st_size
                self.logger.info(f"✅ 保存后验证 - 文件大小: {new_size} 字节, 前100字符: {repr(saved_content)}")
                if file_existed and old_size == new_size:
                    self.logger.warning(f"⚠️  警告：文件大小未变化 ({old_size} 字节)，可能未真正更新")
            except Exception as e:
                self.logger.error(f"❌ 保存后验证失败: {html_path}, 错误: {e}")
            
            self.logger.info(f"✅ 保存HTML文件完成: {html_path} ({len(html_content)} 字符)")
        
        # 保存元数据（使用固定文件名，新文件会覆盖旧文件）
        metadata = {
            'url': fetch_result.url,
            'status_code': fetch_result.status_code,
            'headers': fetch_result.headers,
            'fetched_at': fetch_result.fetched_at.isoformat(),
            'hash': content_hash,
            'html_file': str(html_path) if html_path else None,
            'university': university,
            'department': department
        }
        
        metadata_path = storage_path / "metadata.json"
        # 如果文件已存在，记录覆盖信息
        metadata_existed = metadata_path.exists()
        if metadata_existed:
            self.logger.info(f"📝 元数据文件已存在，将覆盖: {metadata_path}")
        else:
            self.logger.info(f"📝 创建新元数据文件: {metadata_path}")
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ 元数据文件写入成功: {metadata_path}")
        except Exception as e:
            self.logger.error(f"❌ 元数据文件写入失败: {metadata_path}, 错误: {e}")
            raise
        
        # 验证元数据文件
        try:
            new_metadata_size = metadata_path.stat().st_size
            self.logger.info(f"✅ 元数据文件大小: {new_metadata_size} 字节")
        except Exception as e:
            self.logger.error(f"❌ 元数据文件验证失败: {metadata_path}, 错误: {e}")
        
        self.logger.info(f"✅ 保存原始页面完成: {fetch_result.url} (hash: {content_hash[:16]}...)")
        
        return {
            'html_path': str(html_path) if html_path else None,
            'metadata_path': str(metadata_path),
            'hash': content_hash,
            'url': fetch_result.url
        }
    
    def load_metadata(self, metadata_path: str) -> Optional[Dict[str, Any]]:
        """
        加载元数据
        
        Args:
            metadata_path: 元数据文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 元数据
        """
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载元数据失败: {metadata_path}, 错误: {e}")
            return None
    
    def get_latest(self, url: str, university: Optional[str] = None, department: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取URL的最新版本
        
        Args:
            url: 页面URL
            university: 大学名称
            department: 系名称
            
        Returns:
            Optional[Dict[str, Any]]: 最新版本的元数据
        """
        storage_path = self._generate_storage_path(url, university, department)
        
        if not storage_path.exists():
            return None
        
        # 使用固定文件名
        metadata_path = storage_path / "metadata.json"
        
        if not metadata_path.exists():
            return None
        
        # 加载元数据
        return self.load_metadata(str(metadata_path))
    
    def _generate_storage_path(
        self,
        url: str,
        university: Optional[str] = None,
        department: Optional[str] = None
    ) -> Path:
        """
        生成存储路径
        
        Args:
            url: 页面URL
            university: 大学名称
            department: 系名称
            
        Returns:
            Path: 存储路径
        """
        if university and department:
            # 使用层级结构：university/department
            safe_university = self._sanitize_filename(university)
            safe_department = self._sanitize_filename(department)
            return self.base_dir / safe_university / safe_department
        else:
            # 使用URL生成路径
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path_parts = [p for p in parsed.path.strip('/').split('/') if p][:2]
            
            if path_parts:
                folder_name = f"{domain}_{'_'.join(path_parts)}"
            else:
                folder_name = domain
            
            safe_folder = self._sanitize_filename(folder_name)
            return self.base_dir / safe_folder
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名（移除非法字符）
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        import re
        # 移除非法字符
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        # 限制长度
        if len(safe) > 100:
            safe = safe[:100]
        return safe.rstrip('_')

