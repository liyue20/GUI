from bs4 import BeautifulSoup, NavigableString, Tag
import re
from typing import Dict, Tuple
import logging
import cssutils

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.NullHandler()
    ]
)

# 禁用cssutils的日志
cssutils.log.setLevel(logging.FATAL)

class HTMLContentAdjuster:
    def __init__(self):
        # 样式配置
        self.style_config = {
            'min_font_size': 13,  # 最小字体大小（px）
            'min_spacing': 4,     # 最小间距（px）
            'scale_steps': [1, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8, 0.78, 0.76, 0.74, 0.72, 0.7, 0.6, 0.5]# 缩放步骤
        }
        
        # 内容权重配置
        self.content_weights = {
            'div': 30,        # 基础容器
            'p': 40,          # 段落
            'section': 35,    # 区域容器
            'h1': 60,         # 一级标题
            'h2': 50,         # 二级标题
            'h3': 45,         # 三级标题
            'h4': 40,         # 四级标题
            'h5': 35,         # 五级标题
            'h6': 30,         # 六级标题
            'ul': 25,         # 无序列表容器
            'ol': 25,         # 有序列表容器
            'li': 35,         # 列表项
            'table': 80,      # 表格容器
            'tr': 30,         # 表格行
            'th': 35,         # 表头单元格
            'td': 35,         # 普通单元格
            'blockquote': 55, # 引用块
            'pre': 50,        # 预格式化文本
            'code': 40,       # 代码块
            'img': 2000,       # 图片
        }
        
        self.css_variables = {}  # 存储CSS变量
        logging.debug("HTMLContentAdjuster 初始化完成")

    def extract_css_variables(self, soup: BeautifulSoup) -> None:
        """从HTML文档中提取CSS变量"""
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_content = style_tag.string
            if style_content:
                # 查找:root中的变量定义
                root_match = re.search(r':root\s*{([^}]+)}', style_content)
                if root_match:
                    root_content = root_match.group(1)
                    # 提取所有变量定义
                    var_matches = re.finditer(r'--([^:]+):\s*([^;]+);', root_content)
                    for match in var_matches:
                        name, value = match.groups()
                        self.css_variables[f'--{name.strip()}'] = value.strip()
        logging.debug(f"提取的CSS变量: {len(self.css_variables)} 个")

    def resolve_css_var(self, value: str) -> str:
        """解析CSS变量引用"""
        if 'var(' not in value:
            return value
            
        var_match = re.search(r'var\((--[^)]+)\)', value)
        if var_match:
            var_name = var_match.group(1)
            return self.css_variables.get(var_name, '0px').replace('px', '')
        return value

    def get_numeric_value(self, value: str) -> float:
        """从CSS值中提取数字"""
        if not value:
            return 0
        # 解析CSS变量
        value = self.resolve_css_var(value)
        # 提取数字
        match = re.search(r'([\d.]+)', value)
        return float(match.group(1)) if match else 0

    def parse_style(self, style_str: str) -> Dict[str, str]:
        """解析内联样式为字典"""
        style = {}
        if not style_str:
            return style
            
        try:
            for item in cssutils.parseStyle(style_str):
                # 解析可能包含CSS变量的值
                value = self.resolve_css_var(item.value)
                style[item.name] = value
            logging.debug(f"解析样式: {style_str} -> {style}")
        except Exception as e:
            logging.error(f"解析样式错误: {e}")
        return style

    def calculate_content_weight(self, element) -> int:
        """计算元素内容的权重"""
        total_weight = 0
        
        if isinstance(element, Tag):
            # 获取样式信息
            style = self.parse_style(element.get('style', ''))
            font_size = self.get_numeric_value(style.get('font-size', '16'))
            font_size_factor = font_size / 16

            # 计算文本内容的权重
            text_content = element.get_text(strip=True)
            text_weight = len(text_content) * 2 * font_size_factor

            # 添加元素基础权重
            tag_name = element.name.lower() if element.name else ''
            base_weight = self.content_weights.get(tag_name, 0)
            total_weight = text_weight + (base_weight * font_size_factor)

            # 处理padding和margin
            padding = self.get_numeric_value(style.get('padding', '0'))
            margin = self.get_numeric_value(style.get('margin', '0'))
            total_weight += (padding + margin) * 4

            # 递归处理子元素
            for child in element.children:
                if isinstance(child, Tag):
                    child_weight = self.calculate_content_weight(child)
                    total_weight += child_weight
                elif isinstance(child, NavigableString) and child.strip():
                    total_weight += len(child.strip()) * font_size_factor

        elif isinstance(element, NavigableString):
            total_weight = len(element.strip()) * 2

        return int(total_weight)

    def get_block_dimensions(self, block) -> Tuple[float, float]:
        """获取块的宽度和高度"""
        style = block.get('style', '')
        width = self.get_numeric_value(re.search(r'width:\s*([^;]+)', style).group(1) if re.search(r'width:\s*([^;]+)', style) else '0')
        height = self.get_numeric_value(re.search(r'height:\s*([^;]+)', style).group(1) if re.search(r'height:\s*([^;]+)', style) else '0')
        return width, height

    def estimate_content_overflow(self, block_dimensions: Tuple[float, float], content_weight: int) -> bool:
        """估算内容是否会溢出"""
        width, height = block_dimensions
        pixel_capacity = (width * height) / 100
        return content_weight > pixel_capacity
    def _parse_style_to_dict(self, style_string: str) -> Dict[str, str]:
        """将style字符串解析为字典"""
        style_dict = {}
        if not style_string:
            return style_dict

        # 分割样式字符串
        pairs = [pair.strip() for pair in style_string.split(';') if pair.strip()]
        for pair in pairs:
            if ':' in pair:
                property_name, value = pair.split(':', 1)
                style_dict[property_name.strip()] = value.strip()
        return style_dict
    def _dict_to_style_string(self, style_dict: Dict[str, str]) -> str:
        """将样式字典转换为style字符串"""
        # 过滤掉空值和重复值
        unique_styles = {}
        for k, v in style_dict.items():
            if v:
                unique_styles[k.strip()] = v.strip()

        # 生成样式字符串，确保不会以分号开头
        if not unique_styles:
            return ""
        return ' '.join(f"{k}: {v};" for k, v in unique_styles.items()).strip()

    def adjust_block_styles(self, block, scale: float) -> None:
        """调整块内元素的样式"""
        # 调整字体大小
        for text_element in block.select('.content, .title-2, .title-3, .title-4'):
            style = self.parse_style(text_element.get('style', ''))
            current_font_size = self.get_numeric_value(style.get('font-size', '16'))
            new_font_size = max(self.style_config['min_font_size'], int(current_font_size * scale))

            # 更新样式字典
            style_dict = self._parse_style_to_dict(text_element.get('style', ''))
            style_dict['font-size'] = f"{new_font_size}px"
            text_element['style'] = self._dict_to_style_string(style_dict)

        # 调整间距
        for element in block.select('.content, .subsection'):
            style = self.parse_style(element.get('style', ''))
            current_padding = self.get_numeric_value(style.get('padding', '6'))
            new_padding = max(self.style_config['min_spacing'], int(current_padding * scale))

            # 更新样式字典
            style_dict = self._parse_style_to_dict(element.get('style', ''))
            style_dict['padding'] = f"{new_padding}px"
            element['style'] = self._dict_to_style_string(style_dict)
            
            # 添加图片缩放处理
        for img_element in block.select('img'):
            style_dict = self._parse_style_to_dict(img_element.get('style', ''))
            
            # 获取当前宽度和高度
            current_width = self.get_numeric_value(style_dict.get('width', img_element.get('width', '0')))
            current_height = self.get_numeric_value(style_dict.get('height', img_element.get('height', '0')))
            
            if current_width and current_height:
                # 计算新的尺寸
                new_width = int(current_width * scale*0.6)
                new_height = int(current_height * scale*0.6)
                
                # 更新样式
                style_dict['width'] = f"{new_width}px"
                style_dict['height'] = f"{new_height}px"
                img_element['style'] = self._dict_to_style_string(style_dict)
                
                # 同时更新img标签的width和height属性
                img_element['width'] = str(new_width)
                img_element['height'] = str(new_height)
            
        
    def adjust_block_styles_old(self, block, scale: float) -> None:
        """调整块内元素的样式"""
        # 调整字体大小
        for text_element in block.select('.content, .title-2, .title-3, .title-4'):
            style = self.parse_style(text_element.get('style', ''))
            current_font_size = self.get_numeric_value(style.get('font-size', '16'))
            new_font_size = max(self.style_config['min_font_size'], int(current_font_size * scale))
            text_element['style'] = f"{text_element.get('style', '').rstrip(';')}; font-size: {new_font_size}px;"

        # 调整间距
        for element in block.select('.content, .subsection'):
            style = self.parse_style(element.get('style', ''))
            current_padding = self.get_numeric_value(style.get('padding', '6'))
            new_padding = max(self.style_config['min_spacing'], int(current_padding * scale))
            element['style'] = f"{element.get('style', '').rstrip(';')}; padding: {new_padding}px;"

    def add_overflow_styles(self, block) -> None:
        """添加溢出处理的样式"""
        current_style = block.get('style', '')
        block['style'] = f"{current_style.rstrip(';')}; overflow-y: auto;"

    def add_custom_scrollbar_style(self, soup) -> None:
        """添加自定义滚动条样式"""
        style_tag = soup.new_tag('style')
        style_tag.string = """
            .block::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            .block::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }
            .block::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }
            .block::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        """
        if soup.head:
            soup.head.append(style_tag)
        else:
            head = soup.new_tag('head')
            head.append(style_tag)
            soup.insert(0, head)

    def process_html(self, html_content: str) -> str:
        """处理HTML内容"""
        logging.info("开始处理HTML内容")
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取CSS变量
        self.extract_css_variables(soup)

        # 处理所有块
        blocks = soup.select('.block')
        logging.debug(f"找到 {len(blocks)} 个块需要处理")

        for idx, block in enumerate(blocks, start=1):
            dimensions = self.get_block_dimensions(block)
            content_weight = self.calculate_content_weight(block)

            if self.estimate_content_overflow(dimensions, content_weight):
                logging.info(f"块 {idx} 检测到内容溢出，开始调整样式")
                overflow_resolved = False

                # 获取当前字体大小
                content_elements = block.select('.content')
                if content_elements:
                    current_style = self.parse_style(content_elements[0].get('style', ''))
                    current_font_size = self.get_numeric_value(current_style.get('font-size', '16'))

                    # 只在字体大小大于最小值时尝试缩放
                    if current_font_size > self.style_config['min_font_size']:
                        for scale in self.style_config['scale_steps']:
                            new_font_size = current_font_size * scale
                            # 如果缩放后的字体小于最小值，跳出循环
                            if new_font_size < self.style_config['min_font_size']:
                                logging.warning(f"块 {idx} 达到最小字体大小限制，添加滚动条")
                                self.add_overflow_styles(block)
                                break

                            logging.debug(f"尝试缩放比例: {scale}")
                            self.adjust_block_styles(block, scale)
                            adjusted_weight = content_weight * scale

                            if not self.estimate_content_overflow(dimensions, adjusted_weight):
                                overflow_resolved = True
                                logging.info(f"使用缩放比例 {scale} 解决了溢出问题")
                                break
                    else:
                        # 如果当前字体已经是最小值，直接添加滚动条
                        logging.warning(f"块 {idx} 字体已经是最小值，直接添加滚动条")
                        self.add_overflow_styles(block)
                        overflow_resolved = True

                # 如果无法通过缩放解决或没有content元素，添加滚动条
                if not overflow_resolved:
                    logging.warning(f"块 {idx} 无法通过缩放解决溢出，添加滚动条")
                    self.add_overflow_styles(block)
            else:
                logging.debug(f"块 {idx} 不需要调整")

        # 添加自定义滚动条样式
        self.add_custom_scrollbar_style(soup)
        logging.info("HTML处理完成")
        return str(soup)




class HTMLContentAdjuster_old:
    def __init__(self):
        # 样式配置
        self.style_config = {
            'min_font_size': 12,  # 最小字体大小（px）
            'min_spacing': 4,    # 最小间距（px）
            'scale_steps': [1, 0.95,0.9, 0.8, 0.79, 0.76,0.7,0.6, 0.5]  # 缩放步骤
        }
        
        # 内容权重配置（用于估算内容量）
        self.content_weights = {
            'p': 50,          # 段落基础权重
            'li': 40,         # 列表项基础权重
            'table': 100,     # 表格基础权重
            'tr': 80,         # 表格行权重
            'h1': 40,         # 一级标题权重
            'h2': 35,         # 二级标题权重
            'h3': 30,         # 三级标题权重
            'h4': 25,         # 四级标题权重
        }

    def calculate_content_weight(self, element) -> int:
        """计算元素内容的权重"""
        total_weight = 0
        
        # 如果是标签元素（Tag），先处理文本内容
        if isinstance(element, Tag):
            # 计算标签中的文本内容的权重
            text_content = element.get_text(strip=True)
            total_weight += len(text_content) * 2
            
            # 添加元素本身的基础权重
            tag_name = element.name.lower() if element.name else ''
            total_weight += self.content_weights.get(tag_name, 0)
            
            # 递归计算子元素的权重
            for child in element.children:
                if isinstance(child, Tag):  # 确保是标签元素
                    total_weight += self.calculate_content_weight(child)
                elif isinstance(child, NavigableString):  # 处理文本节点
                    total_weight += len(child.strip())  # 可以根据需要调整文本节点的权重
                    
        elif isinstance(element, NavigableString):
            # 如果是纯文本节点，计算文本长度的权重
            total_weight += len(element.strip()) * 2  # 或者其他的加权方式
    
        return total_weight

    def get_block_dimensions(self, block) -> Tuple[float, float]:
        """获取块的宽度和高度"""
        style = block.get('style', '')
        width = float(re.search(r'width:\s*([\d.]+)px', style).group(1)) if re.search(r'width:\s*([\d.]+)px', style) else 0
        height = float(re.search(r'height:\s*([\d.]+)px', style).group(1)) if re.search(r'height:\s*([\d.]+)px', style) else 0
        return width, height

    def estimate_content_overflow(self, block_dimensions: Tuple[float, float], content_weight: int) -> bool:
        """估算内容是否会溢出"""
        width, height = block_dimensions
        # 估算每个像素可以容纳的内容权重
        pixel_capacity = (width * height) / 100  # 假设每100平方像素可以容纳1个权重单位
        return content_weight > pixel_capacity

    def add_overflow_styles(self, block) -> None:
        """添加溢出处理的样式"""
        current_style = block.get('style', '')
        # 添加滚动条样式，保持原有的定位样式
        new_style = current_style.rstrip(';') + '; overflow-y: auto;'
        block['style'] = new_style

    def adjust_block_styles(self, block, scale: float) -> None:
        """调整块内元素的样式"""
        # 调整字体大小
        for text_element in block.select('.content,.title-2, .title-3'):
            current_style = text_element.get('style', '') or ''
            font_size = f"font-size: {max(self.style_config['min_font_size'], int(16 * scale))}px;"
            new_style = current_style + font_size
            text_element['style'] = new_style

        # 调整间距
        for element in block.select('.content, .subsection'):
            current_style = element.get('style', '') or ''
            padding = f"padding: {max(self.style_config['min_spacing'], int(6 * scale))}px;"
            new_style = current_style + padding
            element['style'] = new_style

    def process_html(self, html_content: str) -> str:
        """处理HTML内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        blocks = soup.select('.block')
        
        for block in blocks:
            # 获取块的尺寸
            dimensions = self.get_block_dimensions(block)
            
            # 计算内容权重
            content_weight = self.calculate_content_weight(block)
            
            # 检查是否需要处理溢出
            if self.estimate_content_overflow(dimensions, content_weight):
                # 尝试通过缩放解决溢出
                overflow_resolved = False
                for scale in self.style_config['scale_steps']:
                    self.adjust_block_styles(block, scale)
                    # 重新计算调整后的内容权重
                    adjusted_weight = content_weight * scale
                    if not self.estimate_content_overflow(dimensions, adjusted_weight):
                        overflow_resolved = True
                        break
                
                # 如果缩放后仍然溢出，添加滚动条
                if not overflow_resolved:
                    self.add_overflow_styles(block)
        
        return str(soup)

    def add_custom_scrollbar_style(self, soup) -> None:
        """添加自定义滚动条样式"""
        style_tag = soup.new_tag('style')
        style_tag.string = """
            .block::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            .block::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }
            .block::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }
            .block::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        """
        # 将样式标签添加到head中
        soup.head.append(style_tag)
