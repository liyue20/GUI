import json
from collections import namedtuple

style_json= {
  "title": [
    "25px",
    "22px"
  ],
  "content": [
    "16px",
    "15px"
  ],
  "titleColor": [
    "{color.basic.grey.9}",
    "{color.basic.blue.9}"
  ],
  "bodyColor": [
    "{color.basic.grey.8}",
    "{color.basic.blue.8}"
  ],
  "padding": [
    "24px 0",
    "20px 0"
  ],
  "gap": [
    "{dimension.gap.16}",
    "{dimension.gap.12}"
  ],
  "borderRadius": [
    "{dimension.borderradius.24}",
    "{dimension.borderradius.16}"
  ],
  "images": [
    "https://sop-cdn.dingcloud.com/aigui/file/iavj0hefohm7pn0hpxjq5vshknrg3hgn20240829164358504.png",
    "https://sop-cdn.dingcloud.com/aigui/file/b5e366qa60hv4ook8494ww3dyisn74r720240829165508348.png"
  ]
}

image = namedtuple('image', ['url', 'image_width', 'image_height'])
LayoutInfo = namedtuple('LayoutInfo', ['id', 'content_type', 'content_length', 'min_width', 'min_height', "x_position", "y_position", "act_width", "act_height", "title", "content", "image", "url"])

def layout_to_json(layoutInfos, card_width, card_height, style_index):
    result = {
        "datakeys": [],
        "id": "46-1180251514-8231-4989-104615-1366641347119715",
        "name": "card",
        "file-type": "template",
        "theme": "default",
        "layout": {
            "style": {
                "display": "{layout.state.display.flex}",
                "width": f"{card_width}px",
                "height": f"{card_height}px",
                "padding": "10px 0",
                "position": "relative",
                "background": f"url({style_json['images'][style_index]})"
            },
            "children": []
        }
    }

    for info in layoutInfos:
        block = {
            "name": f"block_{info.id}",
            "file-type": "template",
            "layout": {
                "style": {
                    "width": f"{info.act_width}px",
                    "height": f"{info.act_height}px",
                    "left": f"{info.x_position}px",
                    "top": f"{info.y_position}px",
                    "bgr": "None",
                    "padding": style_json['padding'][style_index],
                    "position": "absolute",
                    "overflow-y": "auto",
                    "border": "2px"
                },
                "children": []
            }
        }

        if info.title:
            block["layout"]["children"].append({
                "name": "title",
                "file-type": "cell-element",
                "layout": {
                    f"text-title-{info.id}": {
                        "style": {
                           "display": "{layout.state.display.flex}",
                           "layoutGrow": "{layout.grow.0}",
                           "padding": style_json['padding'][style_index],
                           "justify-content": "center",
                           "font-size": style_json['title'][style_index],
                           "color": style_json['titleColor'][style_index]
                        },
                        "content": [
                            {
                                "value": "fontsize",
                                "element": "font"
                            }
                        ],
                        "children": []
                    }
                },
                "font": {
                      "fontsize": {
                        "default": {
                          "resource": style_json['title'][style_index],
                          "content": info.title,
                          "style": {
                            "large": {
                              "type": "fontSizes",
                              "value": style_json['title'][style_index],
                              "key": "font-fontsize"
                            }
                          }
                        }
                    }
                }
            })

        if info.content:
            block["layout"]["children"].append({
                "name": "content",
                "file-type": "cell-element",
                "layout": {
                    f"text-content-{info.id}":{
                        "style":{
                           "display": "{layout.state.display.flex}",
                           "layoutGrow": "{layout.grow.0}",
                           "padding": style_json['padding'][style_index], 
                           "font-size": style_json['content'][style_index],
                           "color": style_json['bodyColor'][style_index]
                        },
                        "content": [
                            {
                                "value": "fontsize",
                                "element": "font"
                            }
                        ],
                        "children": []
                    }
                },
                "font": {
                      "fontsize": {
                        "default": {
                          "content": info.content,
                          "style": {
                            "large": {
                              "type": "fontSizes",
                              "value": style_json['content'][style_index],
                              "key": "font-fontsize"
                            }
                          }
                        }
                    }
                }
            })

        if info.image:
            for img in info.image:
                block["layout"]["children"].append({
                    "name": "image",
                    "file-type": "cell-element",
                    "layout": {
                        "img-avatar": {
                            "data": [],
                            "resource": "",
                            "type": "container",
                            "content": [
                              {
                                "value": "image",
                                "element": "material"
                              }
                            ],
                            "style": {
                              "display": "{layout.state.display.flex}",
                              "justify-content": "center"
                            }
                          },
                        "style": {},
                        "children": []
                    },
                    "material": {
                          "image": {
                            "default": {
                              "resource": img.url,
                              "type": "img",
                              "data-key": "userAvatar",
                              "style": {
                                "avatar": {
                                  "type": "asset",
                                  "value": img.url,
                                  "key": "material-image"
                                }
                              }
                            }
                          }
                        },
                })

        result["layout"]["children"].append(block)

    return json.dumps(result, indent=2)
