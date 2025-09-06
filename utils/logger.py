import os
from enum import Enum

class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class Logger:
    """简单的日志管理器"""
    
    def __init__(self, name="NZ_ASR", level=LogLevel.INFO):
        self.name = name
        self.level = level
        
        # 从环境变量读取日志级别
        env_level = os.environ.get('NZ_ASR_LOG_LEVEL', 'INFO').upper()
        if env_level == 'DEBUG':
            self.level = LogLevel.DEBUG
        elif env_level == 'WARNING':
            self.level = LogLevel.WARNING
        elif env_level == 'ERROR':
            self.level = LogLevel.ERROR
    
    def _should_log(self, level):
        """判断是否应该输出日志"""
        return level.value >= self.level.value
    
    def debug(self, message):
        """调试信息"""
        if self._should_log(LogLevel.DEBUG):
            print(f"[DEBUG] {self.name}: {message}")
    
    def info(self, message):
        """一般信息"""
        if self._should_log(LogLevel.INFO):
            print(f"[INFO] {self.name}: {message}")
    
    def warning(self, message):
        """警告信息"""
        if self._should_log(LogLevel.WARNING):
            print(f"[WARNING] {self.name}: {message}")
    
    def error(self, message):
        """错误信息"""
        if self._should_log(LogLevel.ERROR):
            print(f"[ERROR] {self.name}: {message}")

# 创建默认日志实例
default_logger = Logger()

# 便捷函数
def debug(message):
    default_logger.debug(message)

def info(message):
    default_logger.info(message)

def warning(message):
    default_logger.warning(message)

def error(message):
    default_logger.error(message)