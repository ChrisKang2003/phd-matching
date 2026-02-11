"""
通用规则解析器
基于语义DOM特征提取教授信息
"""
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag

# 添加 Web_analys 目录到路径
web_analys_dir = Path(__file__).parent.parent
if str(web_analys_dir) not in sys.path:
    sys.path.insert(0, str(web_analys_dir))

from parser.base_parser import BaseParser


class GeneralParser(BaseParser):
    """通用规则解析器 - 基于语义DOM特征"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化通用解析器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger("general_parser")
        
        # 关键词列表
        self.faculty_keywords = ['faculty', 'people', 'staff', 'professor', 'researcher', 'member']
        self.title_keywords = ['professor', 'associate', 'assistant', 'lecturer', 'adjunct', 'research']
        
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """
        解析HTML内容
        
        Args:
            html: HTML内容
            url: 页面URL
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 判断页面类型
            page_type = self._detect_page_type(soup, url)
            
            if page_type == 'faculty_list':
                return self._parse_faculty_list(soup, url)
            elif page_type == 'profile':
                return self._parse_profile(soup, url)
            else:
                return {
                    'page_type': 'unknown',
                    'url': url,
                    'confidence': 0.0,
                    'data': {}
                }
                
        except Exception as e:
            self.logger.error(f"解析HTML失败: {url}, 错误: {e}", exc_info=True)
            return {
                'page_type': 'error',
                'url': url,
                'confidence': 0.0,
                'error': str(e),
                'data': {}
            }
    
    def get_confidence(self, html: str, url: str) -> float:
        """
        获取解析置信度
        
        Args:
            html: HTML内容
            url: 页面URL
            
        Returns:
            float: 置信度（0-1）
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            confidence = 0.0
            debug_info = []
            
            # 检查是否包含faculty相关关键词
            text = soup.get_text().lower()
            found_keyword = False
            for keyword in self.faculty_keywords:
                if keyword in text:
                    confidence += 0.2
                    found_keyword = True
                    debug_info.append(f"找到关键词: {keyword} (+0.2)")
                    break
            
            if not found_keyword:
                debug_info.append("未找到faculty相关关键词")
            
            # 检查是否有mailto链接
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
            if mailto_links:
                confidence += 0.2
                debug_info.append(f"找到 {len(mailto_links)} 个mailto链接 (+0.2)")
            else:
                debug_info.append("未找到mailto链接")
            
            # 检查是否有schema.org Person标记
            person_markers = soup.find_all(attrs={'itemtype': re.compile(r'.*Person', re.I)})
            if person_markers:
                confidence += 0.3
                debug_info.append(f"找到 {len(person_markers)} 个Person标记 (+0.3)")
            else:
                debug_info.append("未找到Person标记")
            
            # 检查是否有card/list结构
            card_elements = soup.find_all(class_=re.compile(r'card|list|item|person', re.I))
            if card_elements:
                confidence += 0.2
                debug_info.append(f"找到 {len(card_elements)} 个card/list元素 (+0.2)")
            else:
                debug_info.append("未找到card/list结构")
            
            # 检查是否有姓名模式（大写字母开头，可能包含中间名）
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
            name_matches = re.findall(name_pattern, text)
            if name_matches:
                confidence += 0.1
                debug_info.append(f"找到 {len(name_matches)} 个姓名模式 (+0.1)")
            else:
                debug_info.append("未找到姓名模式")
            
            # 如果置信度很低，输出调试信息
            if confidence < 0.3:
                self.logger.debug(f"置信度诊断 ({url}): {'; '.join(debug_info)}")
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"计算置信度时出错: {url}, 错误: {e}")
            return 0.0
    
    def _detect_page_type(self, soup: BeautifulSoup, url: str) -> str:
        """
        检测页面类型
        
        Args:
            soup: BeautifulSoup对象
            url: 页面URL
            
        Returns:
            str: 页面类型（'faculty_list' 或 'profile'）
        """
        text = soup.get_text().lower()
        url_lower = url.lower()
        
        # 检查URL和文本中的关键词
        list_indicators = ['faculty', 'people', 'staff', 'directory', 'list', 'members']
        profile_indicators = ['profile', 'bio', 'about', 'research', 'publication']
        
        list_score = sum(1 for indicator in list_indicators if indicator in url_lower or indicator in text)
        profile_score = sum(1 for indicator in profile_indicators if indicator in url_lower or indicator in text)
        
        # 检查是否有多个人员信息（列表页特征）
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        if len(mailto_links) > 1:
            list_score += 2
        
        if list_score > profile_score:
            return 'faculty_list'
        else:
            return 'profile'
    
    def _parse_faculty_list(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        解析faculty列表页
        
        Args:
            soup: BeautifulSoup对象
            url: 页面URL
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        faculty_list = []
        
        # 查找包含faculty信息的容器
        containers = self._find_faculty_containers(soup)
        
        if not containers:
            self.logger.warning(f"未找到faculty容器，尝试备用方法: {url}")
            # 备用方法：尝试查找所有可能包含人员信息的元素
            containers = self._find_faculty_containers_fallback(soup)
        
        self.logger.info(f"🔍 找到 {len(containers)} 个faculty容器")
        
        # 条目级别置信度阈值（从配置读取，默认0.3）
        entry_confidence_threshold = 0.3
        
        extracted_count = 0
        filtered_count = 0
        
        for idx, container in enumerate(containers):
            # 添加调试：显示前几个容器的内容
            if idx < 3:
                container_text = container.get_text()[:200].strip()
                self.logger.debug(f"容器 {idx+1} 前200字符: {repr(container_text)}")
            
            faculty_info = self._extract_faculty_from_container(container)
            if faculty_info:
                extracted_count += 1
                # 检查条目级别置信度
                entry_confidence = faculty_info.get('confidence', 0.0)
                if entry_confidence >= entry_confidence_threshold:
                    faculty_list.append(faculty_info)
                    self.logger.debug(
                        f"✅ 提取条目 {extracted_count}: {faculty_info.get('name')} "
                        f"(置信度: {entry_confidence:.2f})"
                    )
                else:
                    filtered_count += 1
                    self.logger.debug(
                        f"❌ 过滤低置信度条目 {extracted_count}: {faculty_info.get('name')} "
                        f"(置信度: {entry_confidence:.2f} < {entry_confidence_threshold})"
                    )
            else:
                self.logger.debug(f"⚠️  容器 {idx+1} 未提取到有效信息")
        
        # 统计信息
        total_extracted = len(faculty_list)
        avg_confidence = sum(f.get('confidence', 0.0) for f in faculty_list) / total_extracted if total_extracted > 0 else 0.0
        self.logger.info(f"📊 解析统计 - 容器数: {len(containers)}, "
                        f"尝试提取: {extracted_count}, "
                        f"有效条目: {total_extracted}, "
                        f"过滤: {filtered_count}, "
                        f"平均置信度: {avg_confidence:.2f}")
        
        return {
            'page_type': 'faculty_list',
            'url': url,
            'confidence': self.get_confidence(str(soup), url),
            'data': {
                'faculty_list': faculty_list,
                'count': len(faculty_list)
            }
        }
    
    def _parse_profile(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        解析个人profile页
        
        Args:
            soup: BeautifulSoup对象
            url: 页面URL
            
        Returns:
            Dict[str, Any]: 解析结果
        """
        # 提取结构化字段
        structured = self.extract_structured_fields(str(soup))
        
        # 提取文本字段
        text_fields = self.extract_text_fields(str(soup))
        
        return {
            'page_type': 'profile',
            'url': url,
            'confidence': self.get_confidence(str(soup), url),
            'data': {
                **structured,
                **text_fields
            }
        }
    
    def _find_faculty_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """
        查找包含faculty信息的容器
        
        使用更精确的匹配规则，确保容器真的包含人员信息
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            List[Tag]: 容器列表
        """
        containers = []
        
        # 方法1: 查找包含mailto链接的容器（最可靠）
        # 找到mailto链接，然后向上查找包含人员信息的父容器
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        for link in mailto_links:
            # 向上查找父容器（最多向上5层）
            parent = link.parent
            depth = 0
            while parent and depth < 5:
                # 检查父容器是否包含姓名模式
                text = parent.get_text()
                if self._contains_person_info(text):
                    if parent not in containers:
                        containers.append(parent)
                    break
                parent = parent.parent
                depth += 1
        
        # 方法2: 查找schema.org Person标记（结构化数据，最可靠）
        person_markers = soup.find_all(attrs={'itemtype': re.compile(r'.*Person', re.I)})
        for marker in person_markers:
            # 检查是否真的包含人员信息
            text = marker.get_text()
            if self._contains_person_info(text):
                if marker not in containers:
                    containers.append(marker)
        
        # 方法3: 查找包含faculty关键词且包含人员信息的容器
        for keyword in self.faculty_keywords:
            keyword_containers = soup.find_all(class_=re.compile(keyword, re.I))
            keyword_containers.extend(soup.find_all(id=re.compile(keyword, re.I)))
            
            for container in keyword_containers:
                text = container.get_text()
                # 必须包含人员信息（姓名模式或邮箱）
                if self._contains_person_info(text):
                    if container not in containers:
                        containers.append(container)
        
        # 方法4: 查找card/list结构，但必须包含人员信息
        card_elements = soup.find_all(class_=re.compile(r'card|list-item|person|member|faculty-item|profile', re.I))
        for elem in card_elements:
            text = elem.get_text()
            if self._contains_person_info(text):
                if elem not in containers:
                    containers.append(elem)
        
        # 方法5: 查找people-listing中的li元素（NYU等网站使用）
        people_listings = soup.find_all(class_=re.compile(r'people-listing|faculty-list|staff-list', re.I))
        for listing in people_listings:
            # 查找listing中的li元素
            li_elements = listing.find_all('li')
            for li in li_elements:
                text = li.get_text()
                if self._contains_person_info(text):
                    if li not in containers:
                        containers.append(li)
        
        # 去重（基于对象ID）
        seen = set()
        unique_containers = []
        for container in containers:
            container_id = id(container)
            if container_id not in seen:
                seen.add(container_id)
                unique_containers.append(container)
        
        # 进一步优化：如果容器之间有包含关系，只保留最内层的容器
        # 这样可以避免一个教授的容器包含其他教授的信息
        filtered_containers = []
        for container in unique_containers:
            # 检查是否有其他容器包含这个容器
            is_contained = False
            for other in unique_containers:
                if container != other and container in other.descendants:
                    is_contained = True
                    break
            if not is_contained:
                filtered_containers.append(container)
        
        # 如果过滤后容器数量显著减少，使用过滤后的结果
        # 否则使用原始结果（可能页面结构特殊）
        if len(filtered_containers) >= len(unique_containers) * 0.5:
            return filtered_containers
        else:
            return unique_containers
    
    def _find_faculty_containers_fallback(self, soup: BeautifulSoup) -> List[Tag]:
        """
        备用方法：查找包含faculty信息的容器
        使用更宽松的匹配规则
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            List[Tag]: 容器列表
        """
        containers = []
        
        # 查找所有包含链接的div/li/article等容器
        # 这些容器可能包含人员信息
        for tag_name in ['div', 'li', 'article', 'section', 'tr']:
            elements = soup.find_all(tag_name)
            for elem in elements:
                # 检查是否包含姓名模式或邮箱
                text = elem.get_text()
                if self._contains_person_info(text):
                    containers.append(elem)
        
        # 去重
        seen = set()
        unique_containers = []
        for container in containers:
            container_id = id(container)
            if container_id not in seen:
                seen.add(container_id)
                unique_containers.append(container)
        
        return unique_containers[:50]  # 限制数量，避免过多
    
    def _contains_person_info(self, text: str) -> bool:
        """检查文本是否包含人员信息"""
        if not text or len(text) < 10:
            return False
        
        # 检查是否有姓名模式
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        if re.search(name_pattern, text):
            return True
        
        # 检查是否有标准邮箱格式
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            return True
        
        # 检查是否有"xxx at domain.edu"格式的邮箱
        at_pattern = r'\b[A-Za-z0-9._%+-]+\s+at\s+[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(at_pattern, text, re.I):
            return True
        
        return False
    
    def _extract_faculty_from_container(self, container: Tag) -> Optional[Dict[str, Any]]:
        """
        从容器中提取faculty信息
        
        Args:
            container: 容器元素
            
        Returns:
            Optional[Dict[str, Any]]: faculty信息
        """
        faculty_info = {}
        
        # 提取姓名
        name = self._extract_name(container)
        if not name:
            # 添加调试：为什么没有提取到姓名
            container_text = container.get_text()[:200].strip()
            self.logger.debug(f"⚠️  容器未提取到姓名，前200字符: {repr(container_text)}")
            return None  # 没有姓名，跳过
        faculty_info['name'] = name
        
        # 提取职称
        title = self._extract_title(container)
        if title:
            faculty_info['title'] = title
        
        # 提取邮箱
        email = self._extract_email(container)
        if email:
            faculty_info['email'] = email
        
        # 提取个人主页链接（使用语义化特征优先级）
        homepage_link = self._extract_homepage_link(container)
        if homepage_link:
            faculty_info['links'] = [homepage_link]
        
        # 提取研究方向
        research_interests = self._extract_research_interests(container)
        if research_interests:
            faculty_info['research_interests'] = research_interests
        
        # 计算条目置信度
        entry_confidence = self._calculate_entry_confidence(faculty_info)
        faculty_info['confidence'] = entry_confidence
        
        # 调试输出：显示置信度计算详情
        links = faculty_info.get('links', [])
        homepage_found = False
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict) and link.get('type') == 'homepage':
                    homepage_found = True
                    break
        elif isinstance(links, dict):
            homepage_found = bool(links.get('homepage', ''))
        
        self.logger.debug(
            f"📊 置信度计算: {faculty_info.get('name', 'Unknown')} = {entry_confidence:.2f} "
            f"(姓名✓: {bool(name)}, 邮箱✓: {bool(email)}, 主页✓: {homepage_found}, "
            f"职称✓: {bool(title)}, 研究方向✓: {bool(research_interests)})"
        )
        
        return faculty_info
    
    def _calculate_entry_confidence(self, faculty_info: Dict[str, Any]) -> float:
        """
        计算单个faculty条目的置信度
        
        根据提取到的信息计算置信度：
        - 有效姓名: +0.3
        - 有效邮箱: +0.4
        - 个人主页: +0.2
        - 有效职称: +0.05
        - 研究方向: +0.05
        
        Args:
            faculty_info: faculty信息字典
            
        Returns:
            float: 置信度（0-1）
        """
        confidence = 0.0
        
        name = faculty_info.get('name', '').strip()
        email = faculty_info.get('email', '').strip()
        links = faculty_info.get('links', [])
        title = faculty_info.get('title', '').strip()
        research_interests = faculty_info.get('research_interests', [])
        
        # 查找个人主页
        homepage = None
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict) and link.get('type') == 'homepage':
                    homepage = link.get('url', '')
                    break
        elif isinstance(links, dict):
            homepage = links.get('homepage', '')
        
        # 有效姓名（已经通过_looks_like_name验证）
        if name and self._looks_like_name(name):
            confidence += 0.3
        
        # 有效邮箱
        if email:
            # 检查邮箱格式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                confidence += 0.4
        
        # 个人主页
        if homepage:
            confidence += 0.2
        
        # 有效职称（不在黑名单中）
        if title and not self._is_blacklisted_name(title):
            confidence += 0.05
        
        # 研究方向
        if research_interests and len(research_interests) > 0:
            confidence += 0.05
        
        return min(confidence, 1.0)  # 置信度上限为1.0
    
    def _extract_name(self, container: Tag) -> Optional[str]:
        """提取姓名"""
        # 查找h1-h6标签
        for tag in container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = tag.get_text(strip=True)
            if self._looks_like_name(text):
                return text
        
        # 查找strong/b标签
        for tag in container.find_all(['strong', 'b']):
            text = tag.get_text(strip=True)
            if self._looks_like_name(text):
                return text
        
        # 查找p.name或p.bold标签（NYU等网站使用）
        for tag in container.find_all('p', class_=re.compile(r'name|bold', re.I)):
            text = tag.get_text(strip=True)
            if self._looks_like_name(text):
                return text
            # 如果p标签内有a标签，也检查a标签
            a_tag = tag.find('a')
            if a_tag:
                a_text = a_tag.get_text(strip=True)
                if self._looks_like_name(a_text):
                    return a_text
        
        # 查找a标签（可能是个人主页链接，包含姓名）
        for tag in container.find_all('a', href=True):
            text = tag.get_text(strip=True)
            if self._looks_like_name(text):
                return text
        
        # 查找第一个看起来像姓名的文本
        text = container.get_text(strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3]:  # 只检查前3行
            if self._looks_like_name(line):
                return line
        
        return None
    
    def _looks_like_name(self, text: str) -> bool:
        """
        判断文本是否像姓名
        
        检查：
        1. 格式：2-4个单词，每个单词首字母大写
        2. 不在黑名单中（职称、类别、功能词等）
        3. 不包含常见职称关键词
        """
        if not text or len(text) < 2 or len(text) > 50:
            return False
        
        # 姓名模式：2-4个单词，每个单词首字母大写
        name_pattern = r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$'
        if not re.match(name_pattern, text):
            return False
        
        # 黑名单：职称、类别、功能词
        blacklist = {
            # 职称
            'professor', 'associate professor', 'assistant professor', 
            'adjunct professor', 'lecturer', 'teaching assistant',
            'research professor', 'research scientist', 'visiting professor',
            'emeritus professor', 'clinical professor', 'adjunct',
            # 类别
            'faculty', 'visiting faculty', 'adjunct faculty', 'staff',
            'graduate student', 'postdoc', 'postdoctoral',
            # 功能词
            'by keyword', 'search', 'filter', 'sort', 'view all',
            'show more', 'load more', 'next', 'previous',
            # 其他
            'department', 'school', 'college', 'university'
        }
        
        text_lower = text.lower().strip()
        
        # 检查是否完全匹配黑名单
        if text_lower in blacklist:
            return False
        
        # 检查是否包含职称关键词（作为单词的一部分）
        title_keywords = ['professor', 'lecturer', 'adjunct', 'assistant', 'associate', 'faculty']
        words = text_lower.split()
        for word in words:
            for keyword in title_keywords:
                if keyword in word and word != keyword:  # 如果关键词是单词的一部分（如"professors"），也过滤
                    return False
        
        # 检查是否以职称开头或结尾
        if any(text_lower.startswith(kw) or text_lower.endswith(kw) 
               for kw in ['professor', 'lecturer', 'adjunct', 'faculty']):
            return False
        
        return True
    
    def _is_blacklisted_name(self, text: str) -> bool:
        """
        检查文本是否是黑名单中的职称、类别或功能词
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 如果是黑名单词汇，返回True
        """
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # 职称黑名单
        title_keywords = [
            'professor', 'associate professor', 'assistant professor', 'lecturer',
            'adjunct professor', 'visiting professor', 'research professor',
            'emeritus professor', 'dean', 'chair', 'director', 'head', 'instructor',
            'fellow', 'researcher', 'postdoc', 'phd student', 'graduate student'
        ]
        # 类别/功能词黑名单
        other_keywords = [
            'faculty', 'visiting faculty', 'adjunct faculty', 'staff', 'by keyword',
            'search', 'filter', 'sort', 'department', 'program', 'office', 'phone',
            'email', 'website', 'research', 'interests', 'publications', 'courses',
            'about us', 'contact us', 'news', 'events', 'home', 'apply', 'admissions'
        ]
        
        for keyword in title_keywords + other_keywords:
            # 检查是否是精确匹配或以关键词开头/结尾
            if text_lower == keyword or text_lower.startswith(keyword + ' ') or text_lower.endswith(' ' + keyword):
                return True
        
        return False
    
    def _extract_title(self, container: Tag) -> Optional[str]:
        """提取职称"""
        text = container.get_text().lower()
        
        title_patterns = [
            r'(professor|prof\.)',
            r'associate\s+professor',
            r'assistant\s+professor',
            r'lecturer',
            r'adjunct',
            r'research\s+scientist',
            r'research\s+professor'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0).title()
        
        return None
    
    def _extract_email(self, container: Tag) -> Optional[str]:
        """提取邮箱"""
        # 查找mailto链接
        mailto_link = container.find('a', href=re.compile(r'^mailto:'))
        if mailto_link:
            email = mailto_link.get('href', '').replace('mailto:', '')
            return email.strip()
        
        # 查找文本中的邮箱模式（标准格式：xxx@domain.com）
        text = container.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        
        # 查找"xxx at domain.edu"格式（NYU等网站使用）
        # 匹配模式：Email: xxx at domain.edu 或 xxx at domain.edu
        at_pattern = r'\b([A-Za-z0-9._%+-]+)\s+at\s+([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        match = re.search(at_pattern, text, re.I)
        if match:
            email = f"{match.group(1)}@{match.group(2)}"
            self.logger.debug(f"提取到'at'格式邮箱: {email}")
            return email
        
        return None
    
    def _extract_homepage_link(self, container: Tag) -> Optional[Dict[str, str]]:
        """
        提取个人主页链接（仅个人主页，使用语义化特征优先级）
        
        优先级：
        1. 链接文本 = 姓名（最可靠）
        2. 链接在姓名容器内（p.name, h2.name等）
        3. URL模式 + 位置关系（容器内第一个匹配的链接）
        4. URL用户名匹配（从URL提取用户名并验证）
        
        Args:
            container: 容器元素
            
        Returns:
            Optional[Dict[str, str]]: 个人主页链接信息，如果未找到返回None
        """
        # 提取当前容器的姓名（用于验证链接归属）
        container_name = self._extract_name(container)
        if not container_name:
            return None
        
        container_name_lower = container_name.lower().strip()
        name_parts = container_name_lower.split()
        
        # 获取容器内所有链接
        all_links = container.find_all('a', href=True)
        if not all_links:
            return None
        
        # 优先级1：链接文本 = 姓名（最可靠）
        for link in all_links:
            href = link.get('href', '').strip()
            link_text = link.get_text(strip=True)
            
            # 跳过无效链接
            if not href or href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
            
            # 跳过邮箱保护链接
            if '/email-protection' in href or '/cdn-cgi/l/email-protection' in href:
                continue
            
            # 检查链接文本是否与姓名匹配
            if link_text and link_text.lower().strip() == container_name_lower:
                # 验证URL看起来像个人主页
                if any(kw in href.lower() for kw in ['faculty', 'people', 'profile', 'staff', 'member', 'homepage', 'personal', 'website']):
                    return {'url': href, 'text': link_text, 'type': 'homepage'}
        
        # 优先级2：链接在姓名容器内（p.name, h2.name等）
        name_containers = container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span'], 
                                            class_=re.compile(r'name', re.I))
        for name_container in name_containers:
            # 在姓名容器内查找链接
            name_links = name_container.find_all('a', href=True)
            for link in name_links:
                href = link.get('href', '').strip()
                link_text = link.get_text(strip=True)
                
                # 跳过无效链接
                if not href or href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                    continue
                if '/email-protection' in href or '/cdn-cgi/l/email-protection' in href:
                    continue
                
                # 如果链接文本是姓名，直接返回
                if link_text and link_text.lower().strip() == container_name_lower:
                    return {'url': href, 'text': link_text, 'type': 'homepage'}
                
                # 如果链接文本看起来像姓名，也返回
                if link_text and self._looks_like_name(link_text):
                    if container_name_lower and (link_text.lower() in container_name_lower or container_name_lower in link_text.lower()):
                        return {'url': href, 'text': link_text, 'type': 'homepage'}
        
        # 优先级3：URL模式 + 位置关系（容器内第一个匹配的链接）
        homepage_keywords = ['faculty', 'people', 'profile', 'staff', 'member']
        for link in all_links:
            href = link.get('href', '').strip()
            
            # 跳过无效链接
            if not href or href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
            if '/email-protection' in href or '/cdn-cgi/l/email-protection' in href:
                continue
            
            # 检查URL是否包含个人主页关键词
            if any(kw in href.lower() for kw in homepage_keywords):
                # 提取链接文本
                link_text = link.get_text(strip=True)
                
                # 如果链接文本是姓名，直接返回
                if link_text and link_text.lower().strip() == container_name_lower:
                    return {'url': href, 'text': link_text, 'type': 'homepage'}
                
                # 如果链接文本看起来像姓名且匹配，返回
                if link_text and self._looks_like_name(link_text):
                    if container_name_lower and (link_text.lower() in container_name_lower or container_name_lower in link_text.lower()):
                        return {'url': href, 'text': link_text, 'type': 'homepage'}
                
                # 如果链接文本为空或很短，进入优先级4验证
                if not link_text or len(link_text) < 3:
                    # 优先级4：URL用户名匹配
                    url_match = re.search(r'/(?:profile|faculty|people|staff|member)/([^/?#]+)', href.lower())
                    if url_match:
                        username = url_match.group(1).lower()
                        
                        # 验证用户名是否与姓名匹配
                        if len(name_parts) >= 2:
                            first_initial = name_parts[0][0] if name_parts[0] else ''
                            last_name = name_parts[-1]
                            
                            # 严格匹配：用户名必须以首字母+姓氏开头，或包含完整姓氏（且位置靠前）
                            if (first_initial and username.startswith(f"{first_initial}{last_name}")) or \
                               (len(last_name) >= 4 and last_name in username and username.find(last_name) <= len(username) * 0.8):
                                return {'url': href, 'text': link_text or '', 'type': 'homepage'}
        
        return None
    
    def _extract_links(self, container: Tag) -> List[Dict[str, str]]:
        """
        提取链接（个人主页、实验室、Google Scholar等）
        
        注意：此方法保留用于向后兼容，但推荐使用 _extract_homepage_link 只提取个人主页
        """
        links = []
        seen_urls = set()  # 用于去重
        
        # 提取当前容器的姓名（用于验证链接归属）
        container_name = self._extract_name(container)
        container_name_lower = container_name.lower() if container_name else ""
        
        all_links = container.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '').strip()
            link_text = link.get_text(strip=True)
            text_lower = link_text.lower()
            
            # 跳过空链接
            if not href:
                continue
            
            # 跳过邮箱链接（已在_extract_email中处理）
            if href.startswith('mailto:'):
                continue
            
            # 跳过电话链接
            if href.startswith('tel:'):
                continue
            
            # 跳过JavaScript链接
            if href.startswith('javascript:') or href.startswith('#'):
                continue
            
            # 跳过邮箱保护链接（Cloudflare等）
            if '/email-protection' in href or '/cdn-cgi/l/email-protection' in href:
                continue
            
            # 对于空文本的链接，需要更严格的验证
            # 如果链接文本为空，且不是明确的个人主页标记（如homepage、personal等），需要验证归属
            if not link_text:
                # 如果URL包含profile等关键词，需要验证归属（在后面的逻辑中处理）
                # 如果URL不包含这些关键词，直接跳过
                if not any(kw in href.lower() for kw in ['profile', 'faculty', 'people', 'staff', 'member', 'homepage', 'personal', 'website']):
                    continue
            
            # 去重：相同URL只保留一个
            if href in seen_urls:
                continue
            seen_urls.add(href)
            
            link_info = {'url': href, 'text': link_text}
            
            # 个人主页（明确标记）
            if 'homepage' in text_lower or 'personal' in text_lower or 'website' in text_lower:
                link_info['type'] = 'homepage'
                links.append(link_info)
                continue
            
            # Google Scholar
            if 'scholar' in text_lower or 'scholar.google.com' in href:
                link_info['type'] = 'google_scholar'
                links.append(link_info)
                continue
            
            # 实验室
            if 'lab' in text_lower or 'laboratory' in text_lower:
                link_info['type'] = 'lab'
                links.append(link_info)
                continue
            
            # 个人主页（通过URL模式判断）
            if any(keyword in href.lower() for keyword in ['faculty', 'people', 'profile', 'staff', 'member']):
                # 验证链接归属：必须能够验证链接属于当前教授
                # 方法1: 链接文本看起来像姓名，且与容器姓名匹配
                if link_text and self._looks_like_name(link_text):
                    # 如果链接文本的姓名与容器姓名匹配，或者是容器姓名的一部分
                    if container_name_lower and (link_text.lower() in container_name_lower or container_name_lower in link_text.lower()):
                        link_info['type'] = 'homepage'
                        links.append(link_info)
                        continue
                    # 如果链接文本的姓名与容器姓名不匹配，跳过（可能是其他教授的链接）
                    else:
                        continue
                
                # 方法2: 从URL中提取用户名/ID，检查是否与容器姓名匹配
                # 例如：/profile/sbhatt3 -> sbhatt3，可能与 "Sandeep Bhatt" 匹配
                if not link_text or len(link_text) < 3:
                    # 尝试从URL中提取用户名（profile/username 或 faculty/username 等）
                    url_match = re.search(r'/(?:profile|faculty|people|staff|member)/([^/?#]+)', href.lower())
                    if url_match:
                        username = url_match.group(1)
                        # 检查用户名是否与容器姓名有相似性（例如：sbhatt3 可能与 Sandeep Bhatt 匹配）
                        # 提取姓名的首字母和姓氏
                        if container_name_lower:
                            name_parts = container_name_lower.split()
                            if len(name_parts) >= 2:
                                # 可能的用户名格式：首字母+姓氏（如 sbhatt）
                                first_initial = name_parts[0][0] if name_parts[0] else ''
                                last_name = name_parts[-1].lower()
                                
                                # 更严格的匹配：用户名必须包含姓氏，且姓氏在用户名中的位置合理
                                # 例如：sbhatt3 包含 bhatt，且 bhatt 在开头或紧跟在首字母后
                                username_lower = username.lower()
                                
                                # 检查1: 用户名是否以首字母+姓氏开头（如 sbhatt）
                                if first_initial and username_lower.startswith(f"{first_initial}{last_name}"):
                                    link_info['type'] = 'homepage'
                                    links.append(link_info)
                                    continue
                                
                                # 检查2: 用户名是否包含完整的姓氏（且姓氏长度>=4，避免误匹配）
                                if len(last_name) >= 4 and last_name in username_lower:
                                    # 进一步验证：姓氏在用户名中的位置应该靠前（前80%）
                                    last_name_pos = username_lower.find(last_name)
                                    if last_name_pos >= 0 and last_name_pos <= len(username_lower) * 0.8:
                                        link_info['type'] = 'homepage'
                                        links.append(link_info)
                                        continue
                    
                    # 如果无法验证归属，跳过这个链接（避免包含其他教授的信息）
                    self.logger.debug(f"跳过无法验证归属的链接: {href} (容器姓名: {container_name})")
                    continue
            
            # LinkedIn, Twitter, GitHub等社交媒体
            if 'linkedin.com' in href.lower():
                link_info['type'] = 'linkedin'
                links.append(link_info)
                continue
            elif 'twitter.com' in href.lower() or 'x.com' in href.lower():
                link_info['type'] = 'twitter'
                links.append(link_info)
                continue
            elif 'github.com' in href.lower():
                link_info['type'] = 'github'
                links.append(link_info)
                continue
            
            # 其他链接：只保留看起来像个人主页的链接（链接文本像姓名）
            # 如果链接文本看起来像姓名，且与容器姓名匹配，则保留
            if link_text and self._looks_like_name(link_text):
                if container_name_lower and (link_text.lower() in container_name_lower or container_name_lower in link_text.lower()):
                    link_info['type'] = 'homepage'
                    links.append(link_info)
                    continue
        
        return links
    
    def _extract_research_interests(self, container: Tag) -> Optional[List[str]]:
        """提取研究方向"""
        text = container.get_text()
        
        # 查找"Research Interests"或类似关键词后的内容
        interest_patterns = [
            r'research\s+interests?[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)',
            r'interests?[:\s]+(.+?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in interest_patterns:
            match = re.search(pattern, text, re.I | re.DOTALL)
            if match:
                interests_text = match.group(1).strip()
                # 分割关键词
                interests = [i.strip() for i in re.split(r'[,;]', interests_text) if i.strip()]
                return interests[:10]  # 最多返回10个
        
        return None
    
    def extract_structured_fields(self, html: str) -> Dict[str, Any]:
        """提取结构化字段"""
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('body') or soup
        
        return {
            'name': self._extract_name(container),
            'title': self._extract_title(container),
            'email': self._extract_email(container),
            'links': self._extract_links(container),
            'affiliation': None  # 需要从上下文获取
        }
    
    def extract_text_fields(self, html: str) -> Dict[str, Any]:
        """提取文本字段"""
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('body') or soup
        text = container.get_text()
        
        return {
            'bio': self._extract_bio(text),
            'research_summary': self._extract_research_summary(text),
            'publications': []  # 需要更复杂的解析
        }
    
    def _extract_bio(self, text: str) -> Optional[str]:
        """提取个人简介"""
        # 查找"Biography"或"About"后的内容
        bio_patterns = [
            r'biography[:\s]+(.+?)(?:\n\n|\n[A-Z]{2,}|$)',
            r'about[:\s]+(.+?)(?:\n\n|\n[A-Z]{2,}|$)'
        ]
        
        for pattern in bio_patterns:
            match = re.search(pattern, text, re.I | re.DOTALL)
            if match:
                return match.group(1).strip()[:1000]  # 限制长度
        
        return None
    
    def _extract_research_summary(self, text: str) -> Optional[str]:
        """提取研究摘要"""
        # 查找"Research"后的内容
        research_pattern = r'research[:\s]+(.+?)(?:\n\n|\n[A-Z]{2,}|$)'
        match = re.search(research_pattern, text, re.I | re.DOTALL)
        if match:
            return match.group(1).strip()[:1000]
        
        return None

