# runtime/renderer/screenshot.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import tempfile

class ScreenshotTaker:
    """截图工具类"""
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        # 设置固定窗口大小以确保一致性
        self.chrome_options.add_argument('--window-size=1920,1080')
        
    def take_screenshot(self, html_path: str, output_path: str = None) -> str:
        """
        对指定HTML文件进行截图
        
        Args:
            html_path: HTML文件路径
            output_path: 输出图片路径，如果为None则自动生成
            
        Returns:
            str: 截图文件路径
        """
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # 加载HTML文件
            file_url = f'file://{os.path.abspath(html_path)}'
            driver.get(file_url)
            
            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # 获取页面实际大小
            width = driver.execute_script('return document.documentElement.scrollWidth')
            height = driver.execute_script('return document.documentElement.scrollHeight')
            
            # 设置窗口大小
            driver.set_window_size(width, height)
            
            # 如果没有指定输出路径，创建临时文件
            if not output_path:
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f'screenshot_{os.path.basename(html_path)}.png'
                )
            
            # 截图
            driver.save_screenshot(output_path)
            return output_path
            
        except Exception as e:
            print(f"截图过程发生错误: {str(e)}")
            raise
            
        finally:
            if driver:
                driver.quit()
    
    def take_full_page_screenshot(self, url: str, output_path: str = None) -> str:
        """
        对网页进行全页面截图
        
        Args:
            url: 网页URL
            output_path: 输出图片路径
            
        Returns:
            str: 截图文件路径
        """
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # 获取页面完整高度
            total_height = driver.execute_script(
                'return Math.max('
                'document.body.scrollHeight, '
                'document.documentElement.scrollHeight, '
                'document.body.offsetHeight, '
                'document.documentElement.offsetHeight, '
                'document.body.clientHeight, '
                'document.documentElement.clientHeight'
                ');'
            )
            
            # 设置窗口大小
            driver.set_window_size(1920, total_height)
            
            # 创建输出路径
            if not output_path:
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f'screenshot_{hash(url)}.png'
                )
            
            # 截图
            driver.save_screenshot(output_path)
            return output_path
            
        finally:
            if driver:
                driver.quit()
    
    def take_element_screenshot(self, url: str, selector: str, output_path: str = None) -> str:
        """
        对页面特定元素进行截图
        
        Args:
            url: 网页URL
            selector: CSS选择器
            output_path: 输出图片路径
            
        Returns:
            str: 截图文件路径
        """
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # 等待元素可见
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # 创建输出路径
            if not output_path:
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f'element_screenshot_{hash(url)}_{hash(selector)}.png'
                )
            
            # 元素截图
            element.screenshot(output_path)
            return output_path
            
        finally:
            if driver:
                driver.quit()