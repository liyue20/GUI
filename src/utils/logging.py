import os
import logging
from datetime import datetime

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def setup_logger():
    # 定义日志目录为项目根目录下的 "../data_utils/logging"
    log_dir = os.path.join(project_root, 'data_utils', 'logging')

    # 创建日志目录（如果不存在）
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成当天日期为日志文件名
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f"{log_date}_logging.log")
    
    # 配置日志记录器
    logger = logging.getLogger('project_logger')
    logger.setLevel(logging.DEBUG)  # 设置最低日志级别

    # 创建文件处理器并设置格式
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # 将所有级别的日志写入文件

    # # 创建控制台处理器（输出到控制台）
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)  # 控制台输出INFO及以上级别日志

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)

    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        # logger.addHandler(console_handler)

    return logger
