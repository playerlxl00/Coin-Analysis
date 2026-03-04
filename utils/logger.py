# utils/logger.py
import logging
import sys
from datetime import datetime

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    设置日志记录器
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加handler
    logger.addHandler(console_handler)
    
    # 可选：添加文件handler
    # file_handler = logging.FileHandler(f'logs/monitor_{datetime.now().strftime("%Y%m%d")}.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    return logger

# 创建一个默认的logger
default_logger = setup_logger("new_pair_monitor")
