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
            'h1': 100,         # 一级标题
            'h2': 90,         # 二级标题
            'h3': 80,         # 三级标题
            'h4': 70,         # 四级标题
            'h5': 60,         # 五级标题
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
        for text_element in block.select('.content,.title-1, .title-2, .title-3, .title-4'):
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


class HTMLContentAdjuster_script:
    def __init__(self):
        # 样式配置
        self.style_config = {
            'min_font_size': 13,  # 最小字体大小（px）
            'min_spacing': 4,     # 最小间距（px）
            'scale_steps': [1, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8]
        }
        
        self.css_variables = {}  # 存储CSS变量
        logging.debug("HTMLContentAdjuster 初始化完成")

    def extract_css_variables(self, soup: BeautifulSoup) -> None:
        """从HTML文档中提取CSS变量"""
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_content = style_tag.string
            if style_content:
                root_match = re.search(r':root\s*{([^}]+)}', style_content, re.DOTALL)
                if root_match:
                    root_content = root_match.group(1)
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
        value = self.resolve_css_var(value)
        match = re.search(r'([\d.]+)', value)
        return float(match.group(1)) if match else 0

    def parse_style(self, style_str: str) -> Dict[str, str]:
        """解析内联样式为字典"""
        style = {}
        if not style_str:
            return style
            
        try:
            for item in cssutils.parseStyle(style_str):
                value = self.resolve_css_var(item.value)
                style[item.name] = value
            logging.debug(f"解析样式: {style_str} -> {style}")
        except Exception as e:
            logging.error(f"解析样式错误: {e}")
        return style

    def _parse_style_to_dict(self, style_string: str) -> Dict[str, str]:
        """将style字符串解析为字典"""
        style_dict = {}
        if not style_string:
            return style_dict

        pairs = [pair.strip() for pair in style_string.split(';') if pair.strip()]
        for pair in pairs:
            if ':' in pair:
                property_name, value = pair.split(':', 1)
                style_dict[property_name.strip()] = value.strip()
        return style_dict

    def _dict_to_style_string(self, style_dict: Dict[str, str]) -> str:
        """将样式字典转换为style字符串"""
        unique_styles = {}
        for k, v in style_dict.items():
            if v:
                unique_styles[k.strip()] = v.strip()

        if not unique_styles:
            return ""
        return ' '.join(f"{k}: {v};" for k, v in unique_styles.items()).strip()

    def adjust_block_styles(self, block, scale: float) -> None:
        """调整块内元素的样式"""
        style_dict = self._parse_style_to_dict(block.get('style', ''))
        
        # 只处理特殊情况，如图片缩放
        for img_element in block.select('img'):
            img_style_dict = self._parse_style_to_dict(img_element.get('style', ''))
            
            # 获取当前宽度和高度
            current_width = self.get_numeric_value(img_style_dict.get('width', img_element.get('width', '0')))
            current_height = self.get_numeric_value(img_style_dict.get('height', img_element.get('height', '0')))
            
            if current_width and current_height:
                # 计算新的尺寸
                new_width = int(current_width * scale)
                new_height = int(current_height * scale)
                
                # 更新样式
                img_style_dict['width'] = f"{new_width}px"
                img_style_dict['height'] = f"{new_height}px"
                img_element['style'] = self._dict_to_style_string(img_style_dict)
                
                # 更新img标签的属性
                img_element['width'] = str(new_width)
                img_element['height'] = str(new_height)

    def inject_overflow_detection_script(self, soup: BeautifulSoup) -> None:
        """注入检测溢出的JavaScript脚本"""
        script = soup.new_tag('script')
        script.string = """
        function detectOverflow() {
            const blocks = document.querySelectorAll('.block');
            blocks.forEach(block => {
                // 获取块的实际尺寸和内容尺寸
                const isOverflowing = block.scrollHeight > block.clientHeight;
                const overflowData = {
                    isOverflowing: isOverflowing,
                    scrollHeight: block.scrollHeight,
                    clientHeight: block.clientHeight,
                    difference: block.scrollHeight - block.clientHeight
                };
                
                // 将溢出信息存储为数据属性
                block.setAttribute('data-overflow', JSON.stringify(overflowData));
                
                if (isOverflowing) {
                    // 可以直接在这里添加溢出类
                    block.classList.add('needs-adjustment');
                }
            });
        }
        
        // 页面加载完成后执行检测
        window.addEventListener('load', detectOverflow);
        // 窗口大小改变时重新检测
        window.addEventListener('resize', detectOverflow);
        """
        if soup.head:
            soup.head.append(script)
            logging.debug("溢出检测脚本已注入到<head>。")
        else:
            head = soup.new_tag('head')
            head.append(script)
            soup.insert(0, head)
            logging.debug("溢出检测脚本已注入到新创建的<head>。")

    def add_initial_styles(self, soup: BeautifulSoup) -> None:
        """添加初始样式，包括自动调整的CSS规则"""
        style = soup.new_tag('style')
        style.string = """
            .block {
                transition: all 0.3s ease;
                position: relative;
            }
            
            /* 更细致的缩放控制 */
            .block.needs-adjustment {
                transform-origin: top left;
            }
            
            .block.needs-adjustment .content {
                font-size: 0.9em;
                line-height: 1.4;
            }
            
            .block.needs-adjustment .title-2 {
                font-size: 0.95em;
                margin-bottom: 0.5em;
            }
            
            .block.needs-adjustment .title-3,
            .block.needs-adjustment .title-4 {
                font-size: 0.92em;
                margin-bottom: 0.4em;
            }
            
            .block.needs-adjustment .content,
            .block.needs-adjustment .subsection {
                padding: 4px;
            }
            
            .block.needs-adjustment img {
                max-width: 90%;
                height: auto;
            }
            
            /* 滚动条样式 */
            .block.needs-adjustment {
                overflow-y: auto;
                max-height: 100%;
            }
        """
        if soup.head:
            soup.head.append(style)
            logging.debug("初始样式已注入到<head>。")
        else:
            head = soup.new_tag('head')
            head.append(style)
            soup.insert(0, head)
            logging.debug("初始样式已注入到新创建的<head>。")

    def add_custom_scrollbar_style(self, soup: BeautifulSoup) -> None:
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
            logging.debug("自定义滚动条样式已注入到<head>。")
        else:
            head = soup.new_tag('head')
            head.append(style_tag)
            soup.insert(0, head)
            logging.debug("自定义滚动条样式已注入到新创建的<head>。")

    def inject_baidu_map_api_script(self, soup: BeautifulSoup) -> None:
        """注入百度地图API脚本到<body>末尾"""
        # 检查是否已经存在百度地图API脚本
        api_script_src_pattern = re.compile(r'//api\.map\.baidu\.com/api\?type=webgl&v=1\.0&ak=SWOC1ml97B11kOlpeDWtLwkLPDEx6Wg3')
        existing_api_scripts = soup.find_all('script', src=api_script_src_pattern)
        if existing_api_scripts:
            logging.debug("百度地图API脚本已存在，跳过注入。")
            return  # API脚本已存在，跳过注入

        # 创建百度地图API脚本
        api_script = soup.new_tag('script', src="//api.map.baidu.com/api?type=webgl&v=1.0&ak=SWOC1ml97B11kOlpeDWtLwkLPDEx6Wg3")
        
        # 注入到<body>末尾
        if soup.body:
            soup.body.append(api_script)
            logging.debug("百度地图API脚本已注入到<body>末尾。")
        else:
            # 如果没有<body>，创建一个并插入
            body = soup.new_tag('body')
            body.append(api_script)
            soup.append(body)
            logging.debug("百度地图API脚本已注入到新创建的<body>。")

    def inject_map_initialization_script(self, soup: BeautifulSoup) -> None:
        """注入初始化百度地图的JavaScript脚本到<body>末尾"""
        map_divs = soup.find_all('div', id='map')
        if not map_divs:
            logging.debug("未检测到id为'map'的<div>标签，跳过地图脚本注入。")
            return
        
        # 检查是否已经注入了初始化脚本，避免重复注入
        existing_scripts = soup.find_all('script')
        for script in existing_scripts:
            if script.string and 'function initMap()' in script.string:
                logging.debug("初始化百度地图的脚本已存在，跳过注入。")
                return  # 已经注入过，跳过
        
        # 创建初始化地图的脚本
        init_map_script = soup.new_tag('script')
        init_map_script.string = """
        // 初始化百度地图
        function initMap() {
            if (typeof BMapGL === 'undefined') {
                console.error('百度地图API未加载。请检查API密钥和网络连接。');
                return;
            }

            // 创建地图实例
            var map = new BMapGL.Map('map');
            
            // 设置中心点和缩放级别
            var point = new BMapGL.Point(116.404, 39.915); // 北京的经纬度
            map.centerAndZoom(point, 12);

            // 开启鼠标滚轮缩放功能
            map.enableScrollWheelZoom(true);

            // 添加标注点
            var marker = new BMapGL.Marker(point);
            map.addOverlay(marker);
        }

        // 页面加载完成后初始化地图
        window.addEventListener('load', initMap);
        """
        
        # 注入到<body>末尾
        if soup.body:
            soup.body.append(init_map_script)
            logging.debug("初始化百度地图的脚本已注入到<body>末尾。")
        else:
            # 如果没有<body>，创建一个并插入
            body = soup.new_tag('body')
            body.append(init_map_script)
            soup.append(body)
            logging.debug("初始化百度地图的脚本已注入到新创建的<body>。")

    def process_html(self, html_content: str) -> str:
        """处理HTML内容"""
        logging.info("开始处理HTML内容")
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取CSS变量
        self.extract_css_variables(soup)
        
        # 注入溢出检测脚本
        self.inject_overflow_detection_script(soup)
        
        # 检查是否存在 <div id="map">，如果存在则注入百度地图API脚本和初始化脚本
        map_div = soup.find('div', id='map')
        if map_div:
            logging.debug("检测到 <div id='map'> 标签，准备注入百度地图API脚本和初始化脚本。")
            self.inject_baidu_map_api_script(soup)
            self.inject_map_initialization_script(soup)
        else:
            logging.debug("未检测到 <div id='map'> 标签。")
        
        # 添加初始样式
        self.add_initial_styles(soup)
        
        # 添加自定义滚动条样式
        self.add_custom_scrollbar_style(soup)
        
        logging.info("HTML处理完成")
        return str(soup)

