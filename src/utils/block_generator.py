from typing import List, Dict, Tuple, Optional
from .dimensions import DimensionCalculator
import json
import random
from urllib.request import urlopen
from PIL import Image
import io
from collections import namedtuple
import math
Block = namedtuple('Block', ['id', 'content_type', 'content_length', 'min_width', 'min_height'])

class BlockGenerator:
    def __init__(self, card: Optional[Dict] = None, style_config: Dict = None):
        self.card = card
        self.card_width = card.get('width', 0) if card else 0
        self.card_height = card.get('height', 0) if card else 0
        self.style_config = style_config
        self.dimension_calculator = DimensionCalculator()
        self.use_default_layout = card is None or not card
    
    def update_layout_and_get_content(self, json_content: str, blocks: List[Dict], positions: List[List[float]],container_width: float = 1200) -> List[Dict]:
        """
        更新布局信息并映射到JSON内容
        
        Args:
            json_content: 原始JSON内容
            blocks: 块信息列表
            positions: 布局位置列表 [x, y, width, height]
        
        Returns:
            List[Dict]: 包含布局位置和内容的完整信息列表
        """
        # 解析JSON内容
        sections = json.loads(json_content)
         # 如果 blocks 只有一块，直接跳过布局更新，直接添加内容
        if len(blocks) == 1:
            block = blocks[0]
            idx = block["index"]
            section = sections[idx]
            block["content"] = {
                "title": section["title"],
                "content": section["content"],
                "type": "section"
            }
            block["content"]["subsections"] = section["subsections"]
            return blocks
        # 更新blocks的布局信息并添加内容映射
        for block in blocks:
            idx = block["index"]
            if positions[idx]:  # positions中的顺序与index对应
                # 更新布局信息
                block["position_x"] = positions[idx][0]
                block["position_y"] = positions[idx][1]
                block["act_width"] = positions[idx][2]
                block["act_height"] = positions[idx][3]
                
                # 添加对应的内容信息
                section = sections[idx]
                block["content"] = {
                    "title": section["title"],
                    "content": section["content"],
                    "type": "section"
                }
                block["content"]["subsections"] = section["subsections"]
        
        # 确保 `position_y` 是数值类型
        for block in blocks:
            if isinstance(block.get("position_y"), str) and block["position_y"].replace('.', '').isdigit():
                block["position_y"] = float(block["position_y"])
            elif not isinstance(block.get("position_y"), (int, float)):
                block["position_y"] = 0  # 默认值
        
        # 确保 `position_x` 是数值类型
        for block in blocks:
            if isinstance(block.get("position_x"), str) and block["position_x"].replace('.', '').isdigit():
                block["position_x"] = float(block["position_x"])
            elif not isinstance(block.get("position_x"), (int, float)):
                block["position_x"] = 0  # 默认值
        
        # 检查 blocks 是否为空
        if not blocks:
            print("Warning: No blocks to process.")
            return blocks
        
        try:
            # 找到最顶部的行
            top_row_y = min(block["position_y"] for block in blocks)
            
            # 找到属于顶部行的 blocks
            top_row_blocks = [block for block in blocks if block["position_y"] == top_row_y]
        
            # 调整顶部 blocks 的 y 坐标
            #for block in top_row_blocks:
                #block["position_y"] = max(10, block["position_y"] - 200)
                #block["position_y"] = min(10, block["position_y"] )
            
            
            # 找到最左部的行
            left_row_x = min(block["position_x"] for block in blocks)
            
            # 找到属于左部行的 blocks
            left_row_blocks = [block for block in blocks if block["position_x"] ==  left_row_x]
        
            # 调整左部 blocks 的 x 坐标
            for block in left_row_blocks:
                block["position_x"] = min(20, block["position_x"] )
            
            # 找到最右部的列
            right_row_x = max(block["position_x"] for block in blocks)
            
            # 找到属于最右行的 blocks
            right_row_blocks = [block for block in blocks if block["position_x"] == right_row_x]
        
            # 调整顶部 blocks 的 x 坐标
            for block in right_row_blocks:
                block["position_x"] = min(container_width-block["act_width"]-10, block["position_x"] )
        except Exception as e:
            print(f"Error during layout adjustment: {e}")
        
        
        return blocks

  
    def generate_blocks(self, json_content: str) -> Tuple[List[Dict], List[Block]]:
        """
        生成布局信息和Block对象
        
        Args:
            json_content: JSON格式的内容
            
        Returns:
            Tuple[List[Dict], List[Block]]: 布局信息和Block对象的元组
        """
        sections = json.loads(json_content)
        layout_infos = []
        blocks = []

        # 处理非列表输入
        if not isinstance(sections, list):
            sections = [sections]
        # 如果sections为空或只有一个，使用全宽布局

        if self.use_default_layout or len(sections) <= 1:
            for idx, section in enumerate(sections):
                # 创建布局信息
                layout_info = {
                    "id": f"block_{idx}",
                    "index": idx,
                    "min_width": self.card_width,
                    "min_height": self.card_height,  # 可以根据实际需求调整
                    "position_x": 0,
                    "position_y": 0,
                    "act_width": self.card_width,
                    "act_height": self.card_height,
                    "is_single": True
                }
                layout_infos.append(layout_info)
                # 创建Block对象
                content_type = self._determine_block_type(section)
                content_length = self.card_width * self.card_height
                
                block = Block(
                    id=idx,
                    content_type=content_type,
                    content_length=content_length,
                    min_width=self.card_width,
                    min_height=self.card_height
                )
                blocks.append(block)
            
            return layout_infos, blocks
        
        # 随机决定每行最多显示的块数（2-3个）
        max_blocks_per_row = random.randint(2, 3)
        base_width = self.card_width / max_blocks_per_row
        
        for idx, section in enumerate(sections):
            # 计算块的尺寸
            min_width, min_height = self._calculate_section_dimensions(
                section,
                base_width
            )
            
            # 确保最终宽度不超过base_width
            if min_width > base_width:
                min_width, min_height = self._calculate_section_dimensions(
                    section,
                    base_width,
                    force_width=True
                )
            
            # 创建布局信息
            layout_info = {
                "id": f"block_{idx}",
                "index": idx,
                "min_width": min_width,
                "min_height": min_height,
                "position_x": 0,
                "position_y": 0,
                "act_width": min_width,
                "act_height": min_height
            }
            layout_infos.append(layout_info)
            
            # 创建Block对象
            content_type = self._determine_block_type(section)
            content_length = min_width * min_height  # 使用面积作为内容长度
            
            block = Block(
                id=idx,
                content_type=content_type,
                content_length=content_length,
                min_width=min_width,
                min_height=min_height
            )
            blocks.append(block)
        
        return layout_infos, blocks

    def _determine_block_type(self, section: Dict) -> str:
        """
        确定块的类型
        
        Args:
            section: 章节内容
            
        Returns:
            str: 块类型
        """
        # 检查内容类型
        if not section.get("content"):
            return "text"
            
        for content in section["content"]:
            if content["type"] == "img":
                return "image"
            elif content["type"] == "pre":
                return "code"
            elif content["type"] in ["ul", "ol"]:
                return "list"
        
        return "text"

    def _calculate_section_dimensions(
        self, 
        section: Dict, 
        base_width: float,
        force_width: bool = False
    ) -> Tuple[float, float]:
        """计算section的尺寸"""
        # 计算padding
        padding_horizontal = (
            self.style_config["spacing"]["padding"]["left"] +
            self.style_config["spacing"]["padding"]["right"]
        )
        padding_vertical = (
            self.style_config["spacing"]["padding"]["top"] +
            self.style_config["spacing"]["padding"]["bottom"]
        )
        
        # 计算实际可用的内容宽度
        available_width = base_width - padding_horizontal
        title_text = section["title"]["text"]
        
        # 计算标题尺寸
        title_dims = self.dimension_calculator.calculate_text_dimensions(
            title_text,
            self.style_config["font"]["title"],
            available_width
        )
        
        title_width = title_dims["width"]
        
        # 决定内容区域的目标宽度
        if force_width:
            target_content_width = available_width
        else:
            if title_width <= base_width/2:
                target_content_width = base_width * 0.75
            elif title_width <= available_width:
                # 标题未超出可用宽度，使用标题宽度的1.2倍
                target_content_width = min(title_width * 1.2, available_width)
            else:
                # 标题超出，使用可用宽度
                target_content_width = available_width
        
        content_width = 0
        content_height = 0
        
        # 计算内容尺寸
        if "content" in section:
            for content in section["content"]:
                width, height = self._calculate_content_dimensions(
                    content,
                    target_content_width
                )
                content_width = max(content_width, width)
                content_height += height + self.style_config["spacing"]["margin"]["paragraph"]
        
        # 计算最终尺寸（包含padding）
        final_width = max(title_width, content_width) + padding_horizontal
        final_height = (
            title_dims["height"] + 
            self.style_config["spacing"]["margin"]["title_bottom"] + 
            content_height +
            padding_vertical
        )
        # 递归处理subsections
        if "subsections" in section and section["subsections"]:
            for subsection in section["subsections"]:
                sub_width, sub_height = self._calculate_section_dimensions(subsection, base_width)
                final_width = max(final_width, sub_width)  # 子模块可能扩展宽度
                final_height += sub_height  # 累加子模块高度
        
        return final_width, final_height

    def _calculate_content_dimensions(
        self,
        content: Dict,
        available_width: float
    ) -> Tuple[float, float]:
        """计算内容元素的尺寸"""
        content_type = content["type"]
        
        if content_type == "p":
            if "content" in content:
                # 处理混合内容（文本+图片）
                return self._calculate_mixed_content_dimensions(
                    content["content"],
                    available_width
                )
            else:
                # 处理纯文本
                width_usage = random.uniform(0.8, 1.0)
                dims = self.dimension_calculator.calculate_text_dimensions(
                    content["text"],
                    self.style_config["font"]["paragraph"],
                    available_width * width_usage
                )
                return dims["width"], dims["height"]
        
        elif content_type == "img":
            return self._calculate_image_dimensions(content, available_width)
        
        elif content_type == "pre":
            return self._calculate_code_block_dimensions(content, available_width)
        
        elif content_type in ["ul", "ol"]:
            return self._calculate_list_dimensions(content["items"], available_width)
        
        return 0, 0

    def _calculate_mixed_content_dimensions(
        self,
        contents: List[Dict],
        available_width: float
    ) -> Tuple[float, float]:
        """计算混合内容的尺寸"""
        total_height = 0
        max_width = 0
        
        for item in contents:
            if item["type"] == "text":
                dims = self.dimension_calculator.calculate_text_dimensions(
                    item["text"],
                    self.style_config["font"]["paragraph"],
                    available_width
                )
                max_width = max(max_width, dims["width"])
                total_height += dims["height"]
            elif item["type"] == "img":
                width, height = self._calculate_image_dimensions(item, available_width)
                max_width = max(max_width, width)
                total_height += height
        
        return max_width, total_height

    def _calculate_image_dimensions(
        self, 
        content: Dict, 
        available_width: float
    ) -> Tuple[float, float]:
        """计算图片尺寸"""
        if "src" in content:
            # 获取实际图片尺寸
            original_width, original_height = self._get_image_dimensions(content["src"])
            
            # 计算缩放后的尺寸（宽度为available_width的80%）
            target_width = available_width * 0.8
            aspect_ratio = original_height / original_width
            target_height = target_width * aspect_ratio
            
            return target_width, target_height
        
        # 默认尺寸
        return available_width * 0.8, available_width * 0.8 * 0.6

    def _get_image_dimensions(self, image_url: str) -> Tuple[float, float]:
        """获取图片实际尺寸"""
        try:
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
                
            with urlopen(image_url) as response:
                image_data = response.read()
                image = Image.open(io.BytesIO(image_data))
                return float(image.width), float(image.height)
        except Exception as e:
            print(f"Warning: Could not get image dimensions for {image_url}: {e}")
            return 300.0, 200.0

    def _calculate_code_block_dimensions(
        self,
        content: Dict,
        available_width: float
    ) -> Tuple[float, float]:
        """计算代码块的尺寸"""
        code_config = self.style_config["code_block"]
        dims = self.dimension_calculator.calculate_text_dimensions(
            content["text"],
            code_config,
            available_width - 2 * code_config["padding"]
        )
        
        width = dims["width"] + 2 * code_config["padding"]
        height = dims["height"] + 2 * code_config["padding"]
        
        return width, height

    def _calculate_list_dimensions(
        self,
        items: List[Dict],
        available_width: float,
        level: int = 0
    ) -> Tuple[float, float]:
        """计算列表的尺寸"""
        total_height = 0
        max_width = 0
        indent = self.style_config["font"]["list"]["indent"] * level
        bullet_width = self.style_config["font"]["list"]["bullet_width"]
        
        for item in items:
            # 计算列表项文本尺寸
            text_dims = self.dimension_calculator.calculate_text_dimensions(
                item["text"],
                self.style_config["font"]["list"],
                available_width - indent - bullet_width
            )
            
            current_width = text_dims["width"] + indent + bullet_width
            max_width = max(max_width, current_width)
            total_height += text_dims["height"]
            
            # 处理子列表
            if item["sub_items"]:
                sub_width, sub_height = self._calculate_list_dimensions(
                    item["sub_items"],
                    available_width,
                    level + 1
                )
                max_width = max(max_width, sub_width)
                total_height += sub_height
            
            # 添加列表项间距
            total_height += self.style_config["spacing"]["margin"]["list_item"]
        
        return max_width, total_height
