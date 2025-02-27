from typing import List, Dict, Any
from dataclasses import dataclass
from services.style_agent.rule_generator.rule_manager import StyleRuleGenerator  # 导入样式规则生成器
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

    def __init__(self, layout_info: List[Dict], card_size: Dict[str, int], style_generator: StyleRuleGenerator):
        self.layout_info = layout_info
        self.card_size = card_size
        self.use_default_layout = card_size is None
        self.style_generator = style_generator  # 样式生成器实例

    def parse(self) -> Dict:
        """解析布局生成八要素 JSON"""
        try:
            eight_elements_parts = []
            card_wrapper = self._generate_card_wrapper()
            css_variables = self.style_generator.generate_css_variables()
            with open("css_variables.json", "w", encoding="utf-8") as file:
              json.dump(css_variables, file, indent=2, ensure_ascii=False)

            for block in self.layout_info:
                parsed_block = self._parse_block_eight_elements(block,css_variables)
                card_wrapper['layout']['children'].append(parsed_block)

            eight_elements_parts.append(card_wrapper)

            return eight_elements_parts

        except Exception as e:
            raise RuntimeError(f"解析布局失败: {str(e)}")

    def _generate_card_wrapper(self, block: Dict, css_variables: Dict[str, str]) -> Dict:
        """生成卡片容器为八要素格式"""
        card_id = str(uuid.uuid4())
        json_data = {
            "dataKeys": [],
            "id": f"dd-{card_id}",
            "name": "layout",
            "name-zh": "心流视界NPS评分",
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
                    "width": f"{self.card_size['width']}px",
                    "height":  f"{self.card_size['height']}px",
                    "border-width": "0",
                    "border-style": "solid",
                    "border-color": "initial",
                    "boxSizing": "border-box",
                    "borderRadius": "{dimension.borderradius.8}",
                    "background": "#fff",
                    "justify-content": "initial",
                    "position": "absolute",
                    "back-width": f"{self.card_size['width']}px",
                    "back-height":  f"{self.card_size['height']}px",
                    "box-sizing": "border-box",
                    "left": "0px",
                    "top": "0px"
                },
                "children": []
            },
            "events": [{}],
            "description": "心流视界NPS评分"
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
                "name-zh": "心流视界NPS评分",
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
                        "width": f"{block['act_width']}px",
                        "height": f"{block['act_height']}px",
                        "border-width": "0",
                        "border-style": "solid",
                        "border-color": "initial",
                        "boxSizing": "border-box",
                        "borderRadius": "{dimension.borderradius.8}",
                        "background": "#fff",
                        "justify-content": "initial",
                        "position": "absolute",
                        "back-width": f"{block['act_width']}px",
                        "back-height":  f"{block['act_height']}px",
                        "box-sizing": "border-box",
                        "left":f"{block['position_x']}px"if isinstance(block['position_x'], (int, float)) else "0px",
                        "top": f"{block['position_y']}px" if isinstance(block['position_y'], (int, float)) else "0px"
                    },
                    "children": []
                },
                "events": [{}],
                "description": "心流视界NPS评分"
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

            return block_data

        except Exception as e:
            raise RuntimeError(f"解析区块失败 (ID: {block.get('id', 'unknown')}): {str(e)}")

    def _parse_title(self, title: Dict) -> Dict:
        """解析标题内容"""
        return {
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
                        "box-sizing": "border-box"
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
                                    "value": "none",
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
                                    "value": "{font.size.large}",
                                    "type": "fontSizes",
                                    "key": "font-fontsize"
                                }
                            },
                            "resource": "{font.size.large}"
                        },
                        "hover": {
                            "data-key": "",
                            "content": "我是李悦",
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
                }
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
                        if content_item['type'] == 'bold':
                            eight_elements_parts.append(self._parse_bold_text(content_item))
                        elif content_item['type'] == 'img':
                            eight_elements_parts.append(self._parse_image(content_item))

            elif content_type == 'img':
                eight_elements_parts.append(self._parse_image(item))

        return eight_elements_parts

    def _parse_text(self, item: Dict) -> Dict:
        """解析普通文本内容"""
        return {
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
                        "box-sizing": "border-box"
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
                                    "value": "none",
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
                            "content": "我是李悦",
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
                }
            }

    def _parse_bold_text(self, item: Dict) -> Dict:
        """解析粗体文本内容"""
        return {
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
                        "box-sizing": "border-box"
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
                                    "value": "none",
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
                        "visited": {
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


    def _parse_image(self, item: Dict) -> Dict:
        """解析图片内容"""
        return {
            "id": "dd-481efcb7-ce3a-4afe-8ee7-9e8ffcc9d645",
            "name": "background",
            "name-zh": "图片",
            "file-type": "cell-element",
            "layout": {
                "style": {
                    "background-color": [],
                    "font": [],
                    "border": [],
                    "scale": [],
                    "overflow": "hidden",
                    "box-sizing": "border-box"
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
                                "value": item.get("src", ""),
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
            "type": "image",
            "src": item.get("src", ""),
            "alt": item.get("alt", ""),
            "title": item.get("title", ""),
            "style": {
                "width": "100%",
                "objectFit": "cover",
                "marginBottom": "{dimension.gap.4}"
            }
        }