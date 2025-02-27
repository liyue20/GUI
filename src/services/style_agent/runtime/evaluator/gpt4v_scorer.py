# import openai
# import base64
# from selenium import webdriver
# import os
# import tempfile
# from typing import Dict
# import logging

# logger = logging.getLogger(__name__)

# class GPT4VScorer:
#     """使用 GPT-4V 的UI评分器"""
    
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         openai.api_key = api_key
        
#         # 初始化 Chrome 选项
#         self.chrome_options = webdriver.ChromeOptions()
#         self.chrome_options.add_argument('--headless')
#         self.chrome_options.add_argument('--no-sandbox')
#         self.chrome_options.add_argument('--disable-dev-shm-usage')
    
#     def evaluate_design(self, html: str) -> Dict:
#         """
#         评估UI设计
        
#         Args:
#             html: HTML字符串
            
#         Returns:
#             Dict: 包含分数和分析的字典
#         """
#         try:
#             # 1. HTML转图片
#             screenshot = self._html_to_image(html)
            
#             # 2. 图片转base64
#             image_base64 = self._encode_image(screenshot)
            
#             # 3. GPT-4V分析
#             response = self._analyze_with_gpt4v(image_base64)
            
#             # 4. 解析结果
#             result = self._parse_response(response)
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Error in GPT4V evaluation: {str(e)}")
#             return {
#                 'score': 0.0,
#                 'analysis': str(e),
#                 'details': {}
#             }
    
#     def _html_to_image(self, html: str) -> bytes:
#         """HTML转换为图片"""
#         driver = None
#         temp_html = None
#         try:
#             # 创建临时HTML文件
#             with tempfile.NamedTemporaryFile(
#                 mode='w',
#                 suffix='.html',
#                 encoding='utf-8',
#                 delete=False
#             ) as f:
#                 f.write(html)
#                 temp_html = f.name
            
#             # 初始化 WebDriver
#             driver = webdriver.Chrome(options=self.chrome_options)
            
#             # 加载HTML
#             driver.get(f'file://{os.path.abspath(temp_html)}')
            
#             # 获取页面尺寸
#             height = driver.execute_script('return document.documentElement.scrollHeight')
#             width = driver.execute_script('return document.documentElement.scrollWidth')
#             driver.set_window_size(width, height)
            
#             # 截图
#             return driver.get_screenshot_as_png()
            
#         finally:
#             if driver:
#                 driver.quit()
#             if temp_html and os.path.exists(temp_html):
#                 os.remove(temp_html)
    
#     def _encode_image(self, image_bytes: bytes) -> str:
#         """将图片编码为base64"""
#         return base64.b64encode(image_bytes).decode('utf-8')
    
#     def _analyze_with_gpt4v(self, image_base64: str) -> str:
#         """使用GPT-4V分析"""
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4-vision-preview",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": """作为UI设计评分专家，请对给定UI界面进行详细评估。
#                         评分维度：
#                         1. 视觉层次（信息的重要性是否清晰体现）
#                         2. 色彩搭配（颜色是否和谐、对比是否合适）
#                         3. 排版布局（空间利用是否合理、元素是否对齐）
#                         4. 可读性（文字大小、间距是否适宜）
#                         5. 一致性（设计风格是否统一）
                        
#                         请提供：
#                         - 总分（0-100）
#                         - 各维度评分（0-20）
#                         - 具体分析和建议
#                         """
#                     },
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "image",
#                                 "image_url": f"data:image/png;base64,{image_base64}"
#                             }
#                         ]
#                     }
#                 ],
#                 max_tokens=1000
#             )
            
#             return response.choices[0].message.content
            
#         except Exception as e:
#             logger.error(f"GPT-4V API error: {str(e)}")
#             raise
    
#     def _parse_response(self, response: str) -> Dict:
#         """解析GPT-4V响应"""
#         try:
#             import re
            
#             # 提取总分
#             total_score = 0.0
#             total_match = re.search(r'总分[：:]\s*(\d+)', response)
#             if total_match:
#                 total_score = float(total_match.group(1))
            
#             # 提取维度评分
#             dimensions = {
#                 'visual_hierarchy': '视觉层次',
#                 'color_harmony': '色彩搭配',
#                 'layout': '排版布局',
#                 'readability': '可读性',
#                 'consistency': '一致性'
#             }
            
#             detail_scores = {}
#             for key, keyword in dimensions.items():
#                 score_match = re.search(f'{keyword}[：:]\s*(\d+)', response)
#                 if score_match:
#                     detail_scores[key] = float(score_match.group(1))
#                 else:
#                     detail_scores[key] = 0.0
            
#             return {
#                 'score': total_score / 100,  # 归一化到0-1
#                 'analysis': response,
#                 'details': detail_scores
#             }
            
#         except Exception as e:
#             logger.error(f"Error parsing GPT-4V response: {str(e)}")
#             return {
#                 'score': 0.0,
#                 'analysis': response,
#                 'details': {}
#             }