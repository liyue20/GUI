import re
import markdown
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional
import sys
import io

from src.utils.chart_parser import markdown_to_markdown

# 设置默认编码
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 兼容设置 sys.stdout
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
else:
    sys.stdout = sys.stdout  # 如果没有 buffer 属性，保持原始 sys.stdout

class MarkdownParser:
    """Markdown解析器，将Markdown文本转换为结构化JSON"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置解析器状态"""
        self.sections = []
        self.current_section = None
        self.current_subsection = None
    
    def parse_to_json(self, markdown_text: str) -> str:
        """
        将Markdown文本解析为JSON格式
        
        Args:
            markdown_text: Markdown格式的文本
        Returns:
            JSON字符串
        """
        self.reset()
        if isinstance(markdown_text, bytes):
            markdown_text = markdown_text.decode('utf-8')
            
        # 预处理文本
        markdown_text = self._preprocess_text(markdown_text)
        if not markdown_text.strip():
            return json.dumps([], ensure_ascii=False)
        
        # 使用扩展来支持更多Markdown特性
        extensions = [
            'sane_lists',
            'nl2br',
            'extra',
            'fenced_code',
            'tables',
            'def_list',
            'attr_list'
        ]
        
        # 将Markdown转换为HTML
        html = markdown.markdown(markdown_text, extensions=extensions)
        print(html)
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        # 遍历并解析内容
        self._parse_content(soup,markdown_text)
        
        # 确保最后一个section被添加
        if self.current_section:
            self.sections.append(self.current_section)
        
        return json.dumps(self.sections, ensure_ascii=False, indent=2)
    
    def _parse_content(self, soup,markdown_text):
        """解析HTML内容"""
        for element in soup.children:
            if not element.name:  # 跳过空文本节点
                continue
            
            # 处理标题
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                highest_level = self._get_highest_level_header(markdown_text)
                if level == highest_level:  # 最高级标题开始新的主section
                    self._handle_main_section(element)
                else:  # 其他级别标题作为子section
                    self._handle_subsection(element, level)
            # 处理其他内容
            elif self.current_section:
                content = self._parse_element(element)
                if content:
                    # 根据当前上下文决定内容添加位置
                    if self.current_subsection:
                        self.current_subsection["content"].append(content)
                    else:
                        self.current_section["content"].append(content)
    
    def _handle_main_section(self, element):
        """处理主section（h1标题）"""
        # 保存当前section
        if self.current_section:
            self.sections.append(self.current_section)
        
        # 创建新的main section
        self.current_section = {
            "title": {
                "text": element.get_text(strip=True),
                "level": 1
            },
            "content": [],
            "subsections": [],
            "type": "section"
        }
        self.current_subsection = None
    
    def _handle_subsection(self, element, level):
        """处理子section（h2-h6标题）"""
        if not self.current_section:
            # 如果没有主section，创建一个无标题的主section
            self.current_section = {
                "title": {"text": "", "level": 1},
                "content": [],
                "subsections": [],
                "type": "section"
            }
        
        # 创建新的subsection
        self.current_subsection = {
            "title": {
                "text": element.get_text(strip=True),
                "level": level
            },
            "content": [],
            "type": "subsection"
        }
        self.current_section["subsections"].append(self.current_subsection)

    def _get_highest_level_header(self, text: str) -> int:
        """返回文档中最高级标题的层级（1为一级标题，2为二级标题，依此类推）"""
        matches = re.findall(r'(?m)^(#+)', text)  # 匹配所有标题
        if not matches:
            return 1  # 如果没有标题，默认使用一级标题作为最高级别
        levels = [len(match) for match in matches]  # 统计每个标题的层级
        return min(levels)  # 返回最小层级，即最高级的标题

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 1. 先处理原始文本中的换行符
        text = text.replace('\\n', '\n')
        
        # 2. 移除开头和结尾的空白字符
        text = text.strip()
        
        # 3. 检查是否已经是标准的markdown标题格式
        if text.startswith('# '):
            # 如果是标准格式，直接使用
            pass
        elif text.startswith('#'):
            # 如果#后面没有空格，添加空格
            text = '# ' + text[1:].lstrip()
        else:
            # 如果不是标题格式，添加空标题
            text = "# \n" + text
        
        # 4. 按行处理文本
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        
        # 5. 调用markdown处理函数
        text = '\n'.join(lines)
        text = markdown_to_markdown(text)
        
        return text
    
    def _parse_element(self, element) -> Optional[Dict]:
        """解析HTML元素"""
        if not element.name:
            return None
            
        element_handlers = {
            'p': self._parse_paragraph,
            'pre': self._parse_code_block,
            'ul': self._parse_list,
            'ol': self._parse_list,
            'blockquote': self._parse_blockquote,
            'table': self._parse_table,
            'hr': self._parse_hr
        }
        
        handler = element_handlers.get(element.name)
        return handler(element) if handler else None
    

    
    def _parse_paragraph(self, element) -> Dict:
        """解析段落"""
        contents = []
        
        for content in element.children:
            if content.name == 'img':
                contents.append({
                    "type": "img",
                    "src": content.get('src', ''),
                    "alt": content.get('alt', ''),
                    "title": content.get('title', '')
                })
            elif content.name == 'a':
                contents.append({
                    "type": "link",
                    "text": content.get_text(strip=True),
                    "url": content.get('href', '')
                })        
            elif content.name == 'strong' or content.name == 'b':
                contents.append({
                    "type": "bold",
                    "text": content.text.strip()
                })
             # 处理斜体文本
            elif content.name == 'em' or content.name == 'i':
                contents.append({
                    "type": "italic",
                    "text": content.text.strip()
                })
            elif isinstance(content, str) and content.strip():
                contents.append({
                    "type": "text",
                    "text": content.strip()
                })
        
        
        # 根据内容返回适当的结构
        if len(contents) == 1:
            if contents[0]["type"] == ["img", "a","bold", "italic"]:
                return contents[0]
            if contents[0]["type"] == "text":
                return {
                    "type": "p",
                    "text": contents[0]["text"]
                }
        
        return {
            "type": "p",
            "content": contents
        }
    def _parse_link(self, element) -> Dict:
        """解析超链接"""
        return {
            "type": "link",
            "text": element.get_text(strip=True),
            "url": element.get('href', '')
        }    
    def _parse_code_block(self, element) -> Dict:
        """解析代码块"""
        code = element.find('code')
        language = ''
        if code and code.get('class'):
            language = code.get('class')[0].replace('language-', '')
        return {
            "type": "pre",
            "language": language,
            "text": code.text if code else element.text
        }
    
    def _parse_list(self, element) -> Dict:
        """解析列表"""
        return {
            "type": element.name,  # 'ul' 或 'ol'
            "items": self._parse_list_items(element),
            "list_level": 0  # 添加层级信息
        }
    
    def _parse_list_items(self, list_element, level=0) -> List[Dict]:
        """解析列表项，支持混合嵌套的 ul 和 ol 标签"""
        items = []
        for li in list_element.find_all('li', recursive=False):
            # 获取直接文本内容，排除子列表的文本
            item_text = ''
            for content in li.children:
                if isinstance(content, str):
                    item_text += content.strip()
                elif content.name == 'p':
                    item_text += content.get_text(strip=True)
                elif content.name in ['ul', 'ol']:
                    continue
            
            # 创建字典项
            item = {
                "text": item_text.strip(),
                "sub_items": [],
                "list_type": list_element.name,
                "level": level  # 添加层级信息
            }

            # 处理子列表
            for sublist in li.find_all(['ul', 'ol'], recursive=False):
                sub_items = self._parse_list_items(sublist, level + 1)  # 递归时增加层级
                item["sub_items"].extend(sub_items)

            items.append(item)
        return items

    def _parse_blockquote(self, element) -> Dict:
        """解析引用块"""
        return {
            "type": "blockquote",
            "text": element.text.strip()
        }
    
    def _parse_table(self, element) -> Dict:
        """解析表格"""
        headers = []
        rows = []
        
        header_row = element.find('tr')
        if header_row:
            headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        
        for tr in element.find_all('tr')[1:]:
            row = [td.text.strip() for td in tr.find_all('td')]
            if row:
                rows.append(row)
                
        return {
            "type": "table",
            "headers": headers,
            "rows": rows
        }
    
    def _parse_hr(self, element) -> Dict:
        """解析分割线"""
        return {
            "type": "hr"
        }
