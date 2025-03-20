from typing import List, Dict, Any
from dataclasses import dataclass
import html
import json

@dataclass
class Content:
    """内容数据类"""
    type: str
    text: str = None
    title: Dict = None
    content: List[Dict] = None
    subsections: List[Dict] = None
    src: str = None
    alt: str = None
    headers: List[str] = None    # 表格表头
    rows: List[List[str]] = None # 表格行数据
    language: str = None         # 代码语言

class LayoutParser:
    """布局解析器"""
    
    def __init__(self, layout_info: List[Dict], card_size: Dict[str, int]):
        self.layout_info = layout_info
        self.card_size = card_size
        self.use_default_layout = card_size is None or not card_size
    
    def parse(self) -> str:
        """解析布局生成HTML"""
        try:
            html_parts = []
            # 生成卡片容器
            html_parts.append(self._generate_card_wrapper())
            
            # 解析所有区块
            for block in self.layout_info:
                html_parts.append(self._parse_block(block))
                
            # 闭合卡片容器
            html_parts.append('</div>')
            complete_html = '\n'.join(html_parts)

            return complete_html

            
        except Exception as e:
            raise RuntimeError(f"解析布局失败: {str(e)}")
            
    def _generate_card_wrapper(self) -> str:
        """生成卡片容器"""
        if self.use_default_layout:
            return """
            <div class="card" style="
                width: 100%;
                display: flex;
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
            ">
            """
        return f"""
        <div class="card" style="
            width: {self.card_size['width']}px;
            height: {self.card_size['height']}px;
            position: relative;
            overflow: visible;
        ">
        """
    
    def _parse_block(self, block: Dict) -> str:
        """解析区块"""
        try:
            # 生成区块容器
            if self.use_default_layout:
                block_style = """
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                """
            else:
                block_style = f"""
                    position: absolute;
                    left: {block['position_x']}px;
                    top: {block['position_y']}px;
                    width: {block['act_width']}px;
                    height: {block['act_height']}px;
                """
            
            html_parts = [f'<div id="{block["id"]}" class="block" style="{block_style}">']
            
            content = block.get('content', {})
            # 解析标题
            if 'title' in content:
                html_parts.append(self._parse_title(content['title']))
                
            # 解析主要内容
            if 'content' in content:
                html_parts.append(self._parse_content(content['content']))
                
            # 解析子区块
            if 'subsections' in content:
                subsections_wrapper = '<div class="subsections-wrapper" style="display: flex; flex-direction: column; gap: 0.5rem;">' if self.use_default_layout else '<div class="subsections-wrapper">'
                html_parts.append(subsections_wrapper)
                for subsection in content['subsections']:
                    html_parts.append(self._parse_subsection(subsection))
                html_parts.append('</div>')

            html_parts.append('</div>')
            return '\n'.join(html_parts)
            
        except Exception as e:
            raise RuntimeError(f"解析区块失败 (ID: {block.get('id', 'unknown')}): {str(e)}")
    
    def _parse_content(self, content: List) -> str:
        """解析内容"""
        if not content:
            return ''
            
        content_style = "display: flex; flex-direction: column; gap: 0.5rem;" if self.use_default_layout else ""
        html_parts = [f'<div class="content" style="{content_style}">']     
        
        for item in content:
            if not isinstance(item, dict):
                continue
                
            content_type = item.get('type', '')
            
            if content_type == 'p':
                # 处理段落
                if 'text' in item:
                    html_parts.append(f'<p>{html.escape(item["text"])}</p>')
                elif 'content' in item:
                    html_parts.append(self._parse_rich_content(item['content']))
            elif content_type == 'text':
                html_parts.append(f'<p>{html.escape(item.get("text", ""))}</p>')
            elif content_type == 'img':
                html_parts.append(self._parse_image(item))
            elif content_type == 'table':
                html_parts.append(self._parse_table(item))
            elif content_type == 'code':
                html_parts.append(self._parse_code(item))
            elif content_type in ['ul', 'ol']:
                html_parts.append(self._parse_list(item))
            elif content_type == 'link':
                html_parts.append(self._parse_link(item))  # 解析超链接
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _parse_rich_content(self, content: List) -> str:
        """解析富文本内容"""
        rich_parts = []
        
        for item in content:
            if item.get('type') == 'text':
                rich_parts.append(html.escape(item['text']))
            elif item.get('type') == 'bold':
                rich_parts.append(f"<strong>{html.escape(item['text'])}</strong>")
            elif item.get('type') == 'img':
                rich_parts.append(self._parse_image(item))
            elif item.get('type')== 'link':
                rich_parts.append(self._parse_link(item))
        if rich_parts:
            return f"<p>{''.join(rich_parts)}</p>"
        return ''
    
    def _parse_title(self, title: Dict) -> str:
        """解析标题"""
        level = title.get('level', 1)
        text = html.escape(title.get('text', ''))
        return f'<h{level} class="title-{level}">{text}</h{level}>'
    
    def _parse_subsection(self, subsection: Dict) -> str:
        """解析子区块"""
        subsection_style = "display: flex; flex-direction: column; gap: 0.5rem;" if self.use_default_layout else ""
        html_parts = [f'<div class="subsection" style="{subsection_style}">']
        
        # 解析标题
        if 'title' in subsection:
            html_parts.append(self._parse_title(subsection['title']))
            
        # 解析内容
        if 'content' in subsection:
            html_parts.append(self._parse_content(subsection['content']))
            
        html_parts.append('</div>')
        return '\n'.join(html_parts)

    def _parse_link(self, item: Dict) -> str:
        """解析超链接"""
        link_text = html.escape(item.get('text', ''))
        link_url = html.escape(item.get('url', ''))
    
        return f"""
            <a href="{link_url}" class="link">{link_text}</a>
        """

        
    def _parse_image(self, item: Dict) -> str:
        """解析图片"""
        return f"""
        <div class="image-wrapper">
            <img
                src="{item.get('src', '')}"
                alt="{item.get('alt', '')}"
                title="{item.get('title', '')}"
                class="content-image"
            />
        </div>
        """
    
    def _parse_table(self, item: Dict) -> str:
        """解析表格"""
        table_parts = ['<div class="table-wrapper"><table>']
        
        # 表头
        if 'headers' in item and item['headers']:
            table_parts.append('<thead><tr>')
            for header in item['headers']:
                table_parts.append(f'<th>{html.escape(str(header))}</th>')
            table_parts.append('</tr></thead>')
        
        # 表格内容
        if 'rows' in item and item['rows']:
            table_parts.append('<tbody>')
            for row in item['rows']:
                table_parts.append('<tr>')
                for cell in row:
                    table_parts.append(f'<td>{html.escape(str(cell))}</td>')
                table_parts.append('</tr>')
            table_parts.append('</tbody>')
        
        table_parts.append('</table></div>')
        return '\n'.join(table_parts)
    
    def _parse_code(self, item: Dict) -> str:
        """解析代码块"""
        language = item.get('language', 'python')
        code = html.escape(item.get('text', ''))
        
        return f"""
        <div class="code-wrapper">
            <pre class="code-block">
                <code class="language-{language}">{code}</code>
            </pre>
        </div>
        """
    
    def _parse_list(self, item: Dict) -> str:
        """解析列表（有序和无序列表）"""
        list_type = item.get('type', 'ul')  # 默认为无序列表
        items = item.get('items', [])
        
        if not items:
            return ''
            
        html_parts = [f'<{list_type}>']
        
        for list_item in items:
            # 处理主要文本
            item_text = html.escape(list_item.get('text', ''))
            
            # 处理子项（嵌套列表）
            sub_items = list_item.get('sub_items', [])
            if sub_items:
                # 递归处理子列表
                sub_list = {
                    'type': list_type,
                    'items': sub_items
                }
                item_text += self._parse_list(sub_list)
                
            html_parts.append(f'<li>{item_text}</li>')
        
        html_parts.append(f'</{list_type}>')
        return '\n'.join(html_parts)
    
