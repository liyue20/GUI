from typing import Dict, Tuple, List
import math

class DimensionCalculator:
    """尺寸计算工具类"""
    
    @staticmethod
    def calculate_text_dimensions(
        text: str,
        font_config: Dict,
        available_width: float
    ) -> Dict[str, float]:
        """
        计算文本尺寸
        
        Args:
            text: 要计算的文本
            font_config: 字体配置
            available_width: 可用宽度
            
        Returns:
            包含宽度和高度的字典
        """
        avg_char_width = font_config["size"]
        chars_per_line = math.floor(available_width / avg_char_width)
        text_length = len(text)
        num_lines = math.ceil(text_length / chars_per_line)
        line_height = font_config["size"] * font_config["line_height"]
        total_height = num_lines * line_height
        
        return {
            "width": min(text_length * avg_char_width, available_width),
            "height": total_height
        }
    
    @staticmethod
    def calculate_list_dimensions(
        items: List[Dict],
        font_config: Dict,
        available_width: float,
        level: int = 0
    ) -> Tuple[float, float]:
        """计算列表尺寸，包括嵌套列表
        
        Args:
            items: 列表项
            font_config: 字体配置
            available_width: 可用宽度
            level: 嵌套级别
            
        Returns:
            (宽度, 高度) 的元组
        """
        total_height = 0
        max_width = 0
        indent = font_config["indent"] * level
        
        for item in items:
            # 计算当前项的文本尺寸
            item_width = available_width - indent - font_config["bullet_width"]
            text_dims = DimensionCalculator.calculate_text_dimensions(
                item["text"],
                font_config,
                item_width
            )
            
            current_width = text_dims["width"] + indent + font_config["bullet_width"]
            max_width = max(max_width, current_width)
            total_height += text_dims["height"]
            
            # 处理子项
            if item["sub_items"]:
                sub_width, sub_height = DimensionCalculator.calculate_list_dimensions(
                    item["sub_items"],
                    font_config,
                    available_width,
                    level + 1
                )
                max_width = max(max_width, sub_width)
                total_height += sub_height
        
        return max_width, total_height

    @staticmethod
    def calculate_table_dimensions(
        headers: list,
        rows: list,
        table_config: Dict,
        available_width: float
    ) -> Tuple[float, float]:
        """计算表格尺寸"""
        col_count = len(headers)
        row_count = len(rows) + 1  # 包括表头
        
        # 计算列宽（简化处理，假设等宽）
        col_width = (available_width - (col_count + 1) * table_config["border_width"]) / col_count
        
        # 计算行高
        row_height = table_config["font_size"] * table_config["line_height"] + 2 * table_config["cell_padding"]
        
        total_height = (
            row_count * row_height +
            (row_count + 1) * table_config["border_width"]
        )
        
        return available_width, total_height