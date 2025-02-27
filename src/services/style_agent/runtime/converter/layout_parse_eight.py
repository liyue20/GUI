from queue import Full
from typing import List, Dict, Any, Set
from dataclasses import dataclass
import uuid
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
    headers: List[str] = None    
    rows: List[List[str]] = None 
    language: str = None         

class LayoutParser_eight:
    """布局解析器"""

    def __init__(self, layout_info: List[Dict], card_size: Dict[str, int]):
        self.layout_info = layout_info
        self.card_size = card_size
        self.use_default_layout = card_size is None
    def parse(self) -> Dict:
        """解析布局生成八要素 JSON"""
        try:
            print("测试信息222",self.card_size, flush=True)  
            eight_elements_parts = []
            card_wrapper = self._generate_card_wrapper()
            for block in self.layout_info:
                parsed_block = self._parse_block_eight_elements(block)
                card_wrapper['layout']['children'].append(parsed_block)

            eight_elements_parts.append(card_wrapper)

            return eight_elements_parts

        except Exception as e:
            raise RuntimeError(f"解析布局失败: {str(e)}")

    def _generate_card_wrapper(self) -> Dict:
        """生成卡片容器为八要素格式"""
        card_id = str(uuid.uuid4())
        json_data = {
            "dataKeys": [],
            "id": f"dd-{card_id}",
            "name": "layout",
            "name-zh": "底板",
            "file-type": "template",
            "theme": "default",
            "layout": {
                "style": {
                    "display": "{layout.state.display.flex}",
                    "layoutMode": "{layout.direction.NONE}",
                    "layoutWrap": "{layout.wrap.NO_WRAP}",
                    "primaryAxisSizingMode": "fixed",
                    "counterAxisSizingMode": "{layout.sizing.FIXED}",
                    "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                    "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                    "layoutAlign": "{layout.align.y.self.INHERIT}",
                    "align-items": "initial",
                    "layoutGrow": "{layout.grow.0}",
                    "width": f"{self.card_size['width']}px",
                    "height":  f"{self.card_size['height']}px",
                    "border-width": "{dimension.boderwidth.1}",
                    "border-style": "solid",
                    "border-color": "{color.basic.blue.4}",
                    "boxSizing": "border-box",
                    "borderRadius": "{dimension.borderradius.8}",
                    "background": "{color.gradient.gradient.blue}",
                    "justify-content": "initial",
                    "position": "absolute",
                    "back-width": f"{self.card_size['width']}px",
                    "back-height":  f"{self.card_size['height']}px",
                    "box-sizing": "border-box",
                    "left": "0px",
                    "top": "0px",
                    "border-top-left-radius": "{dimension.borderradius.16}",
                    "border-top-right-radius": "{dimension.borderradius.16}",
                    "border-bottom-left-radius": "{dimension.borderradius.16}",
                    "border-bottom-right-radius": "{dimension.borderradius.16}"
                },
                "children": []
            },
            "events": [{}],
            "description": "底板"
        }
        return json_data
    
    def _parse_block_eight_elements(self, block: Dict) -> Dict:
        """解析区块为八要素格式"""
        try:
            block_id = str(uuid.uuid4())
            block_data = {
                "dataKeys": [],
                "id":  f"dd-{block_id}",
                "name": "layout",
                "name-zh": "Block块",
                "file-type": "template",
                "theme": "default",
                "layout": {
                    "style": {
                        "display": "{layout.state.display.flex}",
                        "layoutMode": "{layout.direction.VERTICAL}",
                        "layoutWrap": "{layout.wrap.NO_WRAP}",
                        "primaryAxisSizingMode": "fixed",
                        "counterAxisSizingMode": "{layout.sizing.FIXED}",
                        "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                        "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                        "layoutGrow": "{layout.grow.0}",
                        "width": f"{block['act_width']}px",
                        "height": f"{block['act_height']}px",
                        "border-width": "{dimension.boderwidth.1}",
                        "border-style": "solid",
                        "border-color": "{color.basic.blue.4}",
                        "boxSizing": "border-box",
                        "justify-content": "flex-start",
                        "align-items": "flex-start",
                        "borderRadius": "{dimension.borderradius.8}",
                        "background": "{color.basic.blue.3}",
                        "back-width": f"{block['act_width']}px",
                        "back-height":  f"{block['act_height']}px",
                        "box-sizing": "border-box",
                        "position": "absolute",
                        "left":f"{block['position_x']}px"if isinstance(block['position_x'], (int, float)) else "0px",
                        "top": f"{block['position_y']}px" if isinstance(block['position_y'], (int, float)) else "0px",
                        "border-top-left-radius": "{dimension.borderradius.16}",
                        "border-top-right-radius": "{dimension.borderradius.16}",
                        "border-bottom-left-radius": "{dimension.borderradius.16}",
                        "border-bottom-right-radius": "{dimension.borderradius.16}",
                        "padding-right": "{dimension.gap.12}",#块中左右内边距
                        "padding-left": "{dimension.gap.12}",
                        "overflow": "auto"
                    },
                    "children": []
                },
                "events": [{}],
                "description": "Block块"
            }
            
            # 解析内容
            if 'content' in block:
                # 首先解析标题
                if isinstance(block['content'], dict) and 'title' in block['content']:
                    title_data = self._parse_title(block['content']['title'])
                    block_data['layout']['children'].append(title_data)
                
                # 然后解析正文内容
                if isinstance(block['content'], dict) and 'content' in block['content']:
                    content_children = self._parse_content(block['content']['content'])
                    if content_children:
                        block_data['layout']['children'].extend(content_children)
                
                # 处理子部分 (subsections)
                if isinstance(block['content'], dict) and 'subsections' in block['content']:
                    for subsection in block['content']['subsections']:
                        subsection_children = []
            
                        # 解析子部分的标题
                        if 'title' in subsection:
                            subsection_title_data = self._parse_title(subsection['title'])
                            subsection_children.append(subsection_title_data)
            
                        # 解析子部分的内容
                        if 'content' in subsection:
                            subsection_content_children = self._parse_content(subsection['content'])
                            if subsection_content_children:
                                subsection_children.extend(subsection_content_children)
            
                        # 添加整个子部分的解析结果
                        if subsection_children:
                            block_data['layout']['children'].extend(subsection_children)
                # 处理子部分 (subsections)
                #if isinstance(block['content'], dict) and 'subsections' in block['content']:
                    #for subsection in block['content']['subsections']:
                        # 解析每个子部分的标题
                        #if 'title' in subsection:
                            #subsection_title_data = self._parse_title(subsection['title'])
                            #block_data['layout']['children'].append(subsection_title_data)
                        
                        # 解析子部分的内容
                        #if 'content' in subsection:
                            #subsection_content_children = self._parse_content(subsection['content'])
                            #if subsection_content_children:
                                #block_data['layout']['children'].extend(subsection_content_children)

            return block_data

        except Exception as e:
            raise RuntimeError(f"解析区块失败 (ID: {block.get('id', 'unknown')}): {str(e)}")

    def _parse_title(self, title: Dict) -> Dict:
         # 获取标题的级别，默认为 1
        level = title.get("level", 1)

        # 定义级别与字体大小的映射
        level_to_fontsize = {
            1: "xxl",  # 级别 1 对应 xl
            2: "basic",   # 级别 2 对应 l
            3: "xl",    # 级别 3 对应 xl
            4: "large", # 级别 4 对应 large
            5: "medium",# 级别 5 对应 medium
            6: "small", # 级别 6 对应 small
        }
        # 定义级别与左对齐和居中的映射
        level_to_justify_content = {
            1: "center",  # 级别 1 对应 center
            2: "flex-start",   # 级别 2 对应 flex-start
            3: "flex-start",    # 级别 3 对应flex-start
            4: "flex-start", # 级别 4 对应 flex-start
            5: "flex-start",# 级别 5 对应 flex-start
            6: "flex-start", # 级别 6 对应 flex-start
        }
         # 定义级别与间隙的映射
        level_to_margin = {
            1: "12",  # 级别 1 对应 xl
            2: "10",   # 级别 2 对应 l
            3: "8",    # 级别 3 对应 xl
            4: "6", # 级别 4 对应 large
            5: "4",# 级别 5 对应 medium
            6: "2", # 级别 6 对应 small
        }
        # 根据级别获取字体大小，默认为 "medium"
        font_size = level_to_fontsize.get(level, "medium")
        # 根据级别获取对齐方式，默认为 "flex-start"
        justify_content = level_to_justify_content.get(level,"flex-start")
        margin = level_to_margin.get(level, "8")
        """解析标题内容"""
        return {
                "dataKeys": [],
                "name": "layout",
                "name-zh": "布局",
                "file-type": "template",
                "theme": "default",
                "layout": {
                    "style": {
                        "display": "{layout.state.display.flex}",
                        "layoutMode": "{layout.direction.HORIZONTAL}",
                        "layoutWrap": "{layout.wrap.NO_WRAP}",
                        "primaryAxisSizingMode": "fixed",
                        "counterAxisSizingMode": "{layout.sizing.FIXED}",
                        "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                        "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                        "layoutGrow": "{layout.grow.0}",
                        "boxSizing": "border-box",
                        "border-style": "solid ",
                        "border-width": "0",
                        "border-color": "initial",
                        "height": "auto",
                        "width": "100%",
                        "box-sizing": "border-box",
                        "back-width": "100%",
                        "back-height": "auto",
                        "position": "relative",
                        "margin-bottom": f"{{dimension.gap.{margin}}}",#上下外边距  20  12  8 6 4 2
                        "background": "{color.basic.cyan.4}",#背景颜色
                        "align-items": "flex-start",
                        "justify-content":  f"{justify_content}",#居中或者左对齐
                        "margin-top": f"{{dimension.gap.{margin}}}",
                        "border-top-left-radius": "{dimension.borderradius.4}",#四个角
                        "border-top-right-radius": "{dimension.borderradius.4}",
                        "border-bottom-left-radius": "{dimension.borderradius.4}",
                        "border-bottom-right-radius": "{dimension.borderradius.4}"                    
                    },
                    "children": [
                        {
                            "id": "dd-50915c68-357b-48ec-a46a-35f5d1679e52",
                            "name": "text",
                            "name-zh": "标题",
                            "file-type": "cell-element",
                            "layout": {
                                "style": {
                                    "background-color": [],
                                    "font": [],
                                    "border": [],
                                    "scale": [],
                                    "box-sizing": "border-box",
                                    "position": "relative",
                                    "primaryAxisSizingMode": "fixed"
                                },
                                "text_body": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "text"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                },
                                "text_hyperlink": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "text-decoration": "underline",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "hyperlinktext"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                }
                            },
                            "color": {
                                "text": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "text": {
                                                "value": "{color.basic.opacity.black.100}",#字体颜色
                                                "type": "color",
                                                "key": "color-text"
                                            },
                                            "hyperlinktext": {
                                                "value": "{color.basic.light-blue.5}",
                                                "type": "color",
                                                "key": "color-text"
                                            }
                                        },
                                        "resource": "{color.basic.light-blue.5}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "hyperlinktext": {
                                                "value": "{color.basic.light-blue.4}",
                                                "type": "color",
                                                "key": "color-text"
                                            }
                                        },
                                        "resource": "{color.basic.light-blue.4}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "hyperlinktext": {
                                                "value": "{color.basic.violet.6}",
                                                "type": "color",
                                                "key": "color-text"
                                            }
                                        },
                                        "resource": "{color.basic.violet.6}"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "style": {
                                            "hyperlinktext": {
                                                "value": "{color.basic.light-blue.7}",
                                                "type": "color",
                                                "key": "color-text"
                                            }
                                        },
                                        "resource": "{color.basic.light-blue.7}"
                                    }
                                },
                                "bg": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "",#背景颜色
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    }
                                }
                            },
                            "scale": {
                                "min_height": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.1000}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1000}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    }
                                },
                                "max_width": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    }
                                }
                            },
                            "font": {
                                "fontsize": {
                                    "default": {
                                        "data-key": "",
                                        "content": title.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value":  f"{{font.size.{font_size}}}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource":  f"{{font.size.{font_size}}}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "content": "我是李悦",
                                        "style": {
                                            "fontsize": {
                                                "value":  f"{{font.size.{font_size}}}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource":  f"{{font.size.{font_size}}}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "content": "默认文本",
                                        "style": {
                                            "fontsize": {
                                                "value":  f"{{font.size.{font_size}}}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource":  f"{{font.size.{font_size}}}"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "content": "默认文本",
                                        "style": {
                                            "fontsize": {
                                                "value":  f"{{font.size.{font_size}}}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource":  f"{{font.size.{font_size}}}"
                                    }
                                }
                            }
                        }
                    ]
                },
                "description": "",
                "id": "dd-4d52a865-6881-488f-81a5-9da2300de428",
                "events": [
                    {}
                ]
        }
                    
   

    def _parse_content(self, content: List[Dict]) -> List[Dict]:
        """解析内容为八要素格式"""
        eight_elements_parts = []

        for item in content:
            if not isinstance(item, dict):
                continue

            content_type = item.get('type', '')

            if content_type == 'p':
                if 'text' in item:
                    # 直接文本内容
                    eight_elements_parts.append(self._parse_text(item))
                
                elif 'content' in item:
                    # 复杂内容（包含富文本和图片）
                    for content_item in item['content']:
                        if content_item['type'] == 'text':
                            eight_elements_parts.append(self._parse_text(content_item))
                        if content_item['type'] == 'bold':
                            eight_elements_parts.append(self._parse_bold_text(content_item))
                        elif content_item['type'] == 'img':
                            eight_elements_parts.append(self._parse_image(content_item))
                
            elif content_type == 'img':
                eight_elements_parts.append(self._parse_image(item))
            elif content_type == 'table':
               eight_elements_parts.append(self._parse_table(item))

        return eight_elements_parts
    
    def _parse_text(self, item: Dict) -> Dict:
        """解析普通文本内容"""
        return  {
                "dataKeys": [],
                "name": "layout",
                "name-zh": "布局",
                "file-type": "template",
                "theme": "default",
                "layout": {
                    "style": {
                        "display": "{layout.state.display.flex}",
                        "layoutMode": "{layout.direction.HORIZONTAL}",
                        "layoutWrap": "{layout.wrap.NO_WRAP}",
                        "primaryAxisSizingMode": "fixed",
                        "counterAxisSizingMode": "{layout.sizing.FIXED}",
                        "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                        "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                        "layoutGrow": "{layout.grow.0}",
                        "boxSizing": "border-box",
                        "border-style": "solid ",
                        "border-width": "0",
                        "border-color": "initial",
                        "background": "",
                        "height": "auto",
                        "width": "100%",
                        "box-sizing": "border-box",
                        "back-width": "100%",
                        "back-height": "auto",
                        "position": "relative",
                        "margin-bottom": "{dimension.gap.4}",
                        "align-items": "flex-start",
                        "justify-content":  "flex-start",#左对齐
                        "margin-top":"{dimension.gap.4}",
                        "border-top-left-radius": "{dimension.borderradius.4}",#四个角
                        "border-top-right-radius": "{dimension.borderradius.4}",
                        "border-bottom-left-radius": "{dimension.borderradius.4}",
                        "border-bottom-right-radius": "{dimension.borderradius.4}"                    
                    },
                    "children": [
                      {
                        "id": "dd-50915c68-357b-48ec-a46a-35f5d1679e52",
                            "name": "text",
                            "name-zh": "文本",
                            "file-type": "cell-element",
                            "layout": {
                                "style": {
                                        "background-color": [],
                                        "font": [],
                                        "border": [],
                                        "scale": [],
                                        "box-sizing": "border-box",
                                        "position": "relative",
                                        "primaryAxisSizingMode": "fixed"
                                },
                                "text_body": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "text"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                },
                                "text_hyperlink": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "text-decoration": "underline",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "hyperlinktext"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                }
                            },
                            "color": {
                                "text": {
                        "default": {
                            "data-key": "",
                            "style": {
                                "text": {
                                    "value": "{color.basic.opacity.black.100}",
                                    "type": "color",
                                    "key": "color-text"
                                },
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.5}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.5}"
                        },
                        "hover": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.4}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.4}"
                        },
                        "visited": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.violet.6}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.violet.6}"
                        },
                        "active": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.7}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.7}"
                        }
                    },
                                "bg": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value":"",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    }
                                }
                            },
                            "scale": {
                                "min_height": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.1000}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1000}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    }
                                },
                                "max_width": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    }
                                }
                            },
                            "font": {
                                "fontsize": {
                                    "default": {
                                        "data-key": "",
                                        "content": item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.basic}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.basic}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "content":  item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.basic}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.basic}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "content":  item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.basic}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.basic}"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "content": item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.basic}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.large}"
                                    }
                                }
                            }
                        }
                    ]
                },
                "description": "",
                "id": "dd-4d52a865-6881-488f-81a5-9da2300de428",
                "events": [
                    {}
                ]
        }
    def _parse_bold_text(self, item: Dict) -> Dict:
        """解析普通文本内容"""
        return  {
                "dataKeys": [],
                "name": "layout",
                "name-zh": "布局",
                "file-type": "template",
                "theme": "default",
                "layout": {
                    "style": {
                        "display": "{layout.state.display.flex}",
                        "layoutMode": "{layout.direction.HORIZONTAL}",
                        "layoutWrap": "{layout.wrap.NO_WRAP}",
                        "primaryAxisSizingMode": "fixed",
                        "counterAxisSizingMode": "{layout.sizing.FIXED}",
                        "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                        "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                        "layoutGrow": "{layout.grow.0}",
                        "boxSizing": "border-box",
                        "border-style": "solid ",
                        "border-width": "0",
                        "border-color": "initial",
                        "background": "{color.basic.blue.2}",
                        "height": "auto",
                        "width": "100%",
                        "box-sizing": "border-box",
                        "back-width": "100%",
                        "back-height": "auto",
                        "position": "relative",
                        "margin-bottom": "{dimension.gap.4}",
                        "align-items": "flex-start",
                        "justify-content":  "flex-start",#左对齐
                        "margin-top":"{dimension.gap.4}",
                        "border-top-left-radius": "{dimension.borderradius.4}",#四个角
                        "border-top-right-radius": "{dimension.borderradius.4}",
                        "border-bottom-left-radius": "{dimension.borderradius.4}",
                        "border-bottom-right-radius": "{dimension.borderradius.4}"                    
                    },
                    "children": [
                      {
                        "id": "dd-50915c68-357b-48ec-a46a-35f5d1679e52",
                            "name": "text",
                            "name-zh": "文本",
                            "file-type": "cell-element",
                            "layout": {
                                "style": {
                                        "background-color": [],
                                        "font": [],
                                        "border": [],
                                        "scale": [],
                                        "box-sizing": "border-box",
                                        "position": "relative",
                                        "primaryAxisSizingMode": "fixed"
                                },
                                "text_body": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "text"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                },
                                "text_hyperlink": {
                                    "type": "container",
                                    "content": [
                                        {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    ],
                                    "resource": "",
                                    "data": [],
                                    "style": {
                                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                                        "layoutGrow": "{layout.grow.0}",
                                        "text-decoration": "underline",
                                        "textColor": {
                                            "element": "color",
                                            "value": "text",
                                            "prop": "default",
                                            "token": "hyperlinktext"
                                        },
                                        "fill": {
                                            "element": "color",
                                            "value": "bg",
                                            "prop": "default",
                                            "token": "bg"
                                        },
                                        "fontSizes": {
                                            "element": "font",
                                            "value": "fontsize",
                                            "prop": "default",
                                            "token": "fontsize"
                                        }
                                    },
                                    "children": []
                                }
                            },
                            "color": {
                                "text": {
                        "default": {
                            "data-key": "",
                            "style": {
                                "text": {
                                    "value": "{color.basic.opacity.black.100}",
                                    "type": "color",
                                    "key": "color-text"
                                },
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.5}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.5}"
                        },
                        "hover": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.4}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.4}"
                        },
                        "visited": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.violet.6}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.violet.6}"
                        },
                        "active": {
                            "data-key": "",
                            "style": {
                                "hyperlinktext": {
                                    "value": "{color.basic.light-blue.7}",
                                    "type": "color",
                                    "key": "color-text"
                                }
                            },
                            "resource": "{color.basic.light-blue.7}"
                        }
                    },
                                "bg": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value":"",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "style": {
                                            "bg": {
                                                "value": "none",
                                                "type": "color",
                                                "key": "color-bg"
                                            }
                                        },
                                        "resource": "none"
                                    }
                                }
                            },
                            "scale": {
                                "min_height": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.1000}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1000}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "min_height": {
                                                "value": "{dimension.basic.dimension.72}",
                                                "type": "sizing",
                                                "key": "scale-min_height"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.72}"
                                    }
                                },
                                "max_width": {
                                    "default": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "style": {
                                            "max_width": {
                                                "value": "{dimension.basic.dimension.1200}",
                                                "type": "sizing",
                                                "key": "scale-max_width"
                                            }
                                        },
                                        "resource": "{dimension.basic.dimension.1200}"
                                    }
                                }
                            },
                            "font": {
                                "fontsize": {
                                    "default": {
                                        "data-key": "",
                                        "content": item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.large}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.large}"
                                    },
                                    "hover": {
                                        "data-key": "",
                                        "content":  item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.large}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.large}"
                                    },
                                    "visited": {
                                        "data-key": "",
                                        "content":  item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.large}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.large}"
                                    },
                                    "active": {
                                        "data-key": "",
                                        "content": item.get("text", ""),
                                        "style": {
                                            "fontsize": {
                                                "value": "{font.size.large}",
                                                "type": "fontSizes",
                                                "key": "font-fontsize"
                                            }
                                        },
                                        "resource": "{font.size.large}"
                                    }
                                }
                            }
                        }
                    ]
                },
                "description": "",
                "id": "dd-4d52a865-6881-488f-81a5-9da2300de428",
                "events": [
                    {}
                ]
        }
    
    def _parse_image(self, item: Dict) -> Dict:
        """解析图片内容"""
        return {
            "dataKeys": [],
            "name": "layout", 
            "name-zh": "布局",
            "file-type": "template",
                        "theme": "default",
                        "layout": {
                            "style": {
                                "display": "{layout.state.display.flex}",
                                "layoutMode": "{layout.direction.HORIZONTAL}",
                                "layoutWrap": "{layout.wrap.NO_WRAP}",
                                "primaryAxisSizingMode": "fixed",
                                "counterAxisSizingMode": "{layout.sizing.FIXED}",
                                "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                                "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                                "layoutAlign": "{layout.align.y.self.INHERIT}",
                                "layoutGrow": "{layout.grow.0}",
                                "boxSizing": "border-box",
                                "border-style": "solid ",
                                "border-width": "0",
                                "border-color": "initial",
                                "background": "",
                                "height": "auto",
                                "width": "100%",
                                "box-sizing": "border-box",
                                "back-width": "100%",
                                "back-height": "auto",
                                "position": "relative",
                                "margin-bottom": "{dimension.gap.4}",
                                "align-items": "flex-start",
                                "justify-content":  "flex-start",#左对齐
                                "margin-top":"{dimension.gap.4}",
                                "border-top-left-radius": "{dimension.borderradius.4}",#四个角
                                "border-top-right-radius": "{dimension.borderradius.4}",
                                "border-bottom-left-radius": "{dimension.borderradius.4}",
                                "border-bottom-right-radius": "{dimension.borderradius.4}"                    
                            },
                            "children": [
                                {
                                    "id": "dd-cd927720-ef28-4689-bc4c-6405d8be10b1",
                                    "name": "background",
                                    "name-zh": "背景",
                                    "file-type": "cell-element",
                                    "layout": {
                                        "style": {
                                            "background-color": [],
                                            "font": [],
                                            "border": [],
                                            "scale": [],
                                            "overflow": "hidden",
                                            "box-sizing": "border-box",
                                            "primaryAxisSizingMode": "fixed",
                                            "position": "relative"
                                        },
                                        "background": {
                                            "type": "container",
                                            "content": [
                                                {
                                                    "element": "material",
                                                    "value": "image",
                                                    "prop": "default",
                                                    "token": "image"
                                                }
                                            ],
                                            "resource": "",
                                            "data": [],
                                            "style": {
                                                "display": "{layout.state.display.flex}",
                                                "layoutMode": "{layout.direction.NONE}",
                                                "layoutWrap": "{layout.wrap.NO_WRAP}",
                                                "primaryAxisSizingMode": "{layout.sizing.AUTO}",
                                                "counterAxisSizingMode": "{layout.sizing.FIXED}",
                                                "primaryAxisAlignItems": "{layout.align.x.MIN}",
                                                "counterAxisAlignItems": "{layout.align.y.items.MIN}",
                                                "layoutAlign": "{layout.align.y.self.INHERIT}",
                                                "layoutGrow": "{layout.grow.0}",
                                                "borderColor": {
                                                    "element": "color",
                                                    "value": "border",
                                                    "prop": "default",
                                                    "token": "border"
                                                },
                                                "borderRadius": {
                                                    "element": "shape",
                                                    "value": "borderradius",
                                                    "prop": "default",
                                                    "token": "borderradius"
                                                },
                                                "borderWidth": {
                                                    "element": "shape",
                                                    "value": "borderwidth",
                                                    "prop": "default",
                                                    "token": "borderwidth"
                                                },
                                                "boxShadow": {
                                                    "element": "material",
                                                    "value": "elevation",
                                                    "prop": "default",
                                                    "token": "elevation"
                                                },
                                                "asset": {
                                                    "element": "material",
                                                    "value": "image",
                                                    "prop": "default",
                                                    "token": "image"
                                                }
                                            },
                                            "children": []
                                        }
                                    },
                                    "material": {
                                        "image": {
                                            "default": {
                                                "data-key": "",
                                                "type": "img",
                                                "style": {
                                                    "image": {
                                                        "value":item.get("src", ""),
                                                        "type": "asset",
                                                        "key": "material-image"
                                                    }
                                                },
                                                "resource": item.get("src", "")
                                            },
                                            "loaded": {
                                                "data-key": "",
                                                "type": "img",
                                                "style": {
                                                    "image": {
                                                        "value": item.get("src", ""),
                                                        "type": "asset",
                                                        "key": "material-image"
                                                    }
                                                },
                                                "resource": item.get("src", "")
                                            }
                                        },
                                        "elevation": {
                                            "default": {
                                                "data-key": "",
                                                "style": {
                                                    "elevation": {
                                                        "value": "none",
                                                        "type": "boxShadow",
                                                        "key": "material-elevation"
                                                    }
                                                },
                                                "resource": "none"
                                            },
                                            "loaded": {
                                                "data-key": "",
                                                "style": {
                                                    "elevation": {
                                                        "value": "none",
                                                        "type": "boxShadow",
                                                        "key": "material-elevation"
                                                    }
                                                },
                                                "resource": "none"
                                            }
                                        }
                                    },
                                    "shape": {
                                        "borderradius": {
                                            "default": {
                                                "data-key": "",
                                                "style": {
                                                    "borderradius": {
                                                        "value": "{dimension.borderradius.0}",
                                                        "type": "borderRadius",
                                                        "key": "shape-borderradius"
                                                    }
                                                },
                                                "resource": "{dimension.borderradius.0}"
                                            },
                                            "loaded": {
                                                "data-key": "",
                                                "style": {
                                                    "borderradius": {
                                                        "value": "{dimension.borderradius.0}",
                                                        "type": "borderRadius",
                                                        "key": "shape-borderradius"
                                                    }
                                                },
                                                "resource": "{dimension.borderradius.0}"
                                            }
                                        },
                                        "borderwidth": {
                                            "default": {
                                                "data-key": "",
                                                "style": {
                                                    "borderwidth": {
                                                        "value": "{dimension.boderwidth.0}",
                                                        "type": "borderWidth",
                                                        "key": "shape-borderwidth"
                                                    }
                                                },
                                                "resource": "{dimension.boderwidth.0}"
                                            },
                                            "loaded": {
                                                "data-key": "",
                                                "style": {
                                                    "borderwidth": {
                                                        "value": "{dimension.boderwidth.0}",
                                                        "type": "borderWidth",
                                                        "key": "shape-borderwidth"
                                                    }
                                                },
                                                "resource": "{dimension.boderwidth.0}"
                                            }
                                        }
                                    },
                                    "color": {
                                        "border": {
                                            "default": {
                                                "data-key": "",
                                                "style": {
                                                    "border": {
                                                        "value": "{color.basic.opacity.black.20}",
                                                        "type": "color",
                                                        "key": "color-border"
                                                    }
                                                },
                                                "resource": "{color.basic.opacity.black.20}"
                                            },
                                            "loaded": {
                                                "data-key": "",
                                                "style": {
                                                    "border": {
                                                        "value": "{color.basic.opacity.black.20}",
                                                        "type": "color",
                                                        "key": "color-border"
                                                    }
                                                },
                                                "resource": "{color.basic.opacity.black.20}"
                                            }
                                        }
                                    },
                                    "type": "background",
                                    "state": "default",
                                    "events": [
                                        {}
                                    ]
                                }
                            ]
                        },
                        "description": "",
                        "id": "dd-4d52a865-6881-488f-81a5-9da2300de428",
                        "events": [
                            {}
                        ]
        }
    
    def _parse_table(self,item:Dict) -> Dict:
        """
        根据动态的 month_12 数据生成 JSON 数据结构。
    
        :param month_12: 包含多组日期的列表，每组是一个集合。
        :return: 生成的 JSON 数据结构。
        """
        headers = item["headers"]  # 表头 ['日', '一', '二', ...]
        rows = item["rows"]        # 每行数据 [['1', '2', ...], ['8', '9', ...], ...]
    
        # 按列重新组织数据
        month_calendar = []
        for col_index, header in enumerate(headers):  # 遍历每一列
            column_data = [header]  # 每列的开头是 header
            for row in rows:
                # 如果 row[col_index] 存在，添加；否则填充 '~~'
                column_data.append(row[col_index] if col_index < len(row) and row[col_index] else "~~")
            month_calendar.append(column_data)

        children_layouts = []
    
        # 遍历 month_12，每组生成一个子布局
        for month_set in month_calendar:
            children = [
                {
                    "id": "dd-fbf2847f-9b70-488b-b8b0-1d61f836b21c",
                    "name": "text",
                    "name-zh": "文本",
                    "file-type": "cell-element",
                    "layout": {
                                                        "style": {
                                                            "background-color": [],
                                                            "font": [],
                                                            "border": [],
                                                            "scale": [],
                                                            "box-sizing": "border-box",
                                                            "primaryAxisSizingMode": "fixed",
                                                            "position": "relative"
                                                        },
                                                        "text_body": {
                                                            "type": "container",
                                                            "content": [
                                                                {
                                                                    "element": "font",
                                                                    "value": "fontsize",
                                                                    "prop": "default",
                                                                    "token": "fontsize"
                                                                }
                                                            ],
                                                            "resource": "",
                                                            "data": [],
                                                            "style": {
                                                                "layoutAlign": "{layout.align.y.self.INHERIT}",
                                                                "layoutGrow": "{layout.grow.0}",
                                                                "overflow": "auto",
                                                                "word-break": "break-all",
                                                                "textColor": {
                                                                    "element": "color",
                                                                    "value": "text",
                                                                    "prop": "default",
                                                                    "token": "text"
                                                                },
                                                                "fill": {
                                                                    "element": "color",
                                                                    "value": "bg",
                                                                    "prop": "default",
                                                                    "token": "bg"
                                                                },
                                                                "fontSizes": {
                                                                    "element": "font",
                                                                    "value": "fontsize",
                                                                    "prop": "default",
                                                                    "token": "fontsize"
                                                                }
                                                            },
                                                            "children": []
                                                        },
                                                        "text_hyperlink": {
                                                            "type": "container",
                                                            "content": [
                                                                {
                                                                    "element": "font",
                                                                    "value": "fontsize",
                                                                    "prop": "default",
                                                                    "token": "fontsize"
                                                                }
                                                            ],
                                                            "resource": "",
                                                            "data": [],
                                                            "style": {
                                                                "layoutAlign": "{layout.align.y.self.INHERIT}",
                                                                "layoutGrow": "{layout.grow.0}",
                                                                "text-decoration": "underline",
                                                                "overflow": "auto",
                                                                "word-break": "break-all",
                                                                "textColor": {
                                                                    "element": "color",
                                                                    "value": "text",
                                                                    "prop": "default",
                                                                    "token": "hyperlinktext"
                                                                },
                                                                "fill": {
                                                                    "element": "color",
                                                                    "value": "bg",
                                                                    "prop": "default",
                                                                    "token": "bg"
                                                                },
                                                                "fontSizes": {
                                                                    "element": "font",
                                                                    "value": "fontsize",
                                                                    "prop": "default",
                                                                    "token": "fontsize"
                                                                }
                                                            },
                                                            "children": []
                                                        }
                                                    },
                    "color": {
                                                        "text": {
                                                            "default": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "text": {
                                                                        "value": "{color.basic.opacity.black.100}",
                                                                        "type": "color",
                                                                        "key": "color-text"
                                                                    },
                                                                    "hyperlinktext": {
                                                                        "value": "{color.basic.light-blue.5}",
                                                                        "type": "color",
                                                                        "key": "color-text"
                                                                    }
                                                                },
                                                                "resource": "{color.basic.light-blue.5}"
                                                            },
                                                            "hover": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "hyperlinktext": {
                                                                        "value": "{color.basic.light-blue.4}",
                                                                        "type": "color",
                                                                        "key": "color-text"
                                                                    }
                                                                },
                                                                "resource": "{color.basic.light-blue.4}"
                                                            },
                                                            "visited": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "hyperlinktext": {
                                                                        "value": "{color.basic.violet.6}",
                                                                        "type": "color",
                                                                        "key": "color-text"
                                                                    }
                                                                },
                                                                "resource": "{color.basic.violet.6}"
                                                            },
                                                            "active": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "hyperlinktext": {
                                                                        "value": "{color.basic.light-blue.7}",
                                                                        "type": "color",
                                                                        "key": "color-text"
                                                                    }
                                                                },
                                                                "resource": "{color.basic.light-blue.7}"
                                                            }
                                                        },
                                                        "bg": {
                                                            "default": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "bg": {
                                                                        "value": "",
                                                                        "type": "color",
                                                                        "key": "color-bg"
                                                                    }
                                                                },
                                                                "resource": "none"
                                                            },
                                                            "hover": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "bg": {
                                                                        "value": "none",
                                                                        "type": "color",
                                                                        "key": "color-bg"
                                                                    }
                                                                },
                                                                "resource": "none"
                                                            },
                                                            "visited": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "bg": {
                                                                        "value": "none",
                                                                        "type": "color",
                                                                        "key": "color-bg"
                                                                    }
                                                                },
                                                                "resource": "none"
                                                            },
                                                            "active": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "bg": {
                                                                        "value": "none",
                                                                        "type": "color",
                                                                        "key": "color-bg"
                                                                    }
                                                                },
                                                                "resource": "none"
                                                            }
                                                        }
                                                    },
                    "scale": {
                                                        "min_height": {
                                                            "default": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "min_height": {
                                                                        "value": "{dimension.basic.dimension.72}",
                                                                        "type": "sizing",
                                                                        "key": "scale-min_height"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.72}"
                                                            },
                                                            "hover": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "min_height": {
                                                                        "value": "{dimension.basic.dimension.72}",
                                                                        "type": "sizing",
                                                                        "key": "scale-min_height"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.72}"
                                                            },
                                                            "visited": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "min_height": {
                                                                        "value": "{dimension.basic.dimension.72}",
                                                                        "type": "sizing",
                                                                        "key": "scale-min_height"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.72}"
                                                            }
                                                        },
                                                        "max_width": {
                                                            "default": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "max_width": {
                                                                        "value": "{dimension.basic.dimension.1200}",
                                                                        "type": "sizing",
                                                                        "key": "scale-max_width"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.1200}"
                                                            },
                                                            "hover": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "max_width": {
                                                                        "value": "{dimension.basic.dimension.1200}",
                                                                        "type": "sizing",
                                                                        "key": "scale-max_width"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.1200}"
                                                            },
                                                            "visited": {
                                                                "data-key": "",
                                                                "style": {
                                                                    "max_width": {
                                                                        "value": "{dimension.basic.dimension.1200}",
                                                                        "type": "sizing",
                                                                        "key": "scale-max_width"
                                                                    }
                                                                },
                                                                "resource": "{dimension.basic.dimension.1200}"
                                                            }
                                                        }
                                                    },
                    "font": {
                        "fontsize": {
                            "default": {
                                "data-key": "",
                                "content": day,
                                "style": {
                                                                    "fontsize": {
                                                                        "value": "{font.size.large}",
                                                                        "type": "fontSizes",
                                                                        "key": "font-fontsize"
                                                                    }
                                                                },
                                "resource": "{font.size.large}"
                            },
                            "hover": {
                                "data-key": "",
                                "content": "默认文本",
                                "style": {
                                    "fontsize": {
                                        "value": "{font.size.large}",
                                        "type": "fontSizes",
                                        "key": "font-fontsize"
                                    }
                                },
                                "resource": "{font.size.large}"
                            },
                            "visited": {
                                "data-key": "",
                                "content": "默认文本",
                                "style": {
                                    "fontsize": {
                                        "value": "{font.size.large}",
                                        "type": "fontSizes",
                                        "key": "font-fontsize"
                                    }
                                },
                                "resource": "{font.size.large}"
                            },
                            "active": {
                                "data-key": "",
                                "content": "默认文本",
                                "style": {
                                    "fontsize": {
                                        "value": "{font.size.large}",
                                        "type": "fontSizes",
                                        "key": "font-fontsize"
                                    }
                                },
                                "resource": "{font.size.large}"
                            }
                        }
                    },
                    "type": "text_body",
                    "state": "default",
                    "events": [
                        {}
                    ]
                }for day in month_set]
          
            children_layouts.append(
                 {
                    "dataKeys": [],
                    "name": "layout",
                    "name-zh": "布局",
                    "file-type": "template",
                    "theme": "default",
                    "layout": {
                        "style": {
                            "display": "{layout.state.display.flex}",
                            "layoutMode": "{layout.direction.VERTICAL}",
                            "layoutWrap": "{layout.wrap.NO_WRAP}",
                            "primaryAxisSizingMode": "responsive",
                            "counterAxisSizingMode": "{layout.sizing.FIXED}",
                            "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                            "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                            "layoutAlign": "{layout.align.y.self.INHERIT}",
                            "layoutGrow": "{layout.grow.0}",
                            "boxSizing": "border-box",
                            "border-style": "solid ",
                            "border-width": "0",
                            "border-color": "initial",
                            "height": "auto",
                            "width": "auto",
                            "box-sizing": "border-box",
                            "back-width": "100%",
                            "back-height": "fit-content",
                            "position": "relative",
                            "justify-content": "center",
                            "align-items": "flex-start",
                            "gap": "{dimension.gap.8}",
                            "background": "{color.basic.cyan.3}",
                            "padding-right": "{dimension.gap.4}",
                            "padding-left": "{dimension.gap.4}",
                            "border-top-left-radius": "{dimension.borderradius.8}",
                            "border-top-right-radius": "{dimension.borderradius.8}",
                            "border-bottom-left-radius": "{dimension.borderradius.4}",
                            "border-bottom-right-radius": "{dimension.borderradius.4}"
                        },
                         "children": children
                        
                    },
                    "description": "",
                    "id": "dd-a494e9bc-7a00-4592-9a11-aeb025d3cafa",
                    "events": [
                        {}
                    ]
                })
    
        # 返回最终的 JSON 结构
        return  {
                "dataKeys": [],
                "name": "layout",
                "name-zh": "日历",
                "file-type": "template",
                "theme": "default",
                "layout": {
                    "style": {
                        "display": "{layout.state.display.flex}",
                        "layoutMode": "{layout.direction.HORIZONTAL}",
                        "layoutWrap": "{layout.wrap.NO_WRAP}",
                        "primaryAxisSizingMode": "responsive",
                        "counterAxisSizingMode": "{layout.sizing.FIXED}",
                        "primaryAxisAlignItems": "{layout.align.x.CENTER}",
                        "counterAxisAlignItems": "{layout.align.y.items.CENTER}",
                        "layoutAlign": "{layout.align.y.self.INHERIT}",
                        "layoutGrow": "{layout.grow.0}",
                        "boxSizing": "border-box",
                        "border-style": "solid ",
                        "border-width": "0",
                        "border-color": "initial",
                        "height": "auto",
                        "width": "auto",
                        "box-sizing": "border-box",
                        "back-width": "100%",
                        "back-height": "100%",
                        "position": "relative",
                        "justify-content": "flex-start",
                        "align-items": "flex-start",
                        "padding-bottom": "{dimension.gap.6}",
                        "padding-right": "{dimension.gap.6}",
                        "border-top-left-radius": "{dimension.borderradius.16}",
                        "border-top-right-radius": "{dimension.borderradius.16}",
                        "border-bottom-left-radius": "{dimension.borderradius.16}",
                        "border-bottom-right-radius": "{dimension.borderradius.16}",
                        "padding-left": "{dimension.gap.6}",
                        "padding-top": "{dimension.gap.6}"
                    },
                    "children": children_layouts
                },
                "description": "",
                "id": "dd-b05f00ad-c1",
                "events": [{}]
            }