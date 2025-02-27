from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import os

class WebRenderer:
    """网页渲染器"""
    
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
    def render_to_image(self, html_content: str) -> str:
        """
        渲染HTML内容并生成图片
        
        Args:
            html_content: HTML字符串
            
        Returns:
            str: 生成的图片路径
        """
        temp_html = None
        driver = None
        try:
            # 保存HTML到临时文件
            temp_html = self._save_temp_html(html_content)
            
            # 初始化WebDriver
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # 加载HTML
            driver.get(f'file://{os.path.abspath(temp_html)}')
            
            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # 获取页面尺寸
            height = driver.execute_script('return document.documentElement.scrollHeight')
            width = driver.execute_script('return document.documentElement.scrollWidth')
            driver.set_window_size(width, height)
            
            # 截图
            screenshot_path = os.path.join(
                tempfile.gettempdir(),
                f'screenshot_{hash(html_content)}.png'
            )
            driver.save_screenshot(screenshot_path)
            
            return screenshot_path
            
        finally:
            if driver:
                driver.quit()
            if temp_html and os.path.exists(temp_html):
                os.remove(temp_html)
    
    def _save_temp_html(self, html_content: str) -> str:
        """保存HTML到临时文件"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            encoding='utf-8',
            delete=False
        ) as f:
            f.write(html_content)
            return f.name