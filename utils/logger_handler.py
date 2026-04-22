from datetime import datetime
import logging
import os
from utils.path_tool import get_abs_path

"""日志模块。

目标：
1. 统一控制台与文件日志格式；
2. 避免重复添加 handler；
3. 对外暴露全局 logger 供全项目复用。
"""

#日志保存的根目录
LOG_ROOT = get_abs_path("logs")

#确保日志目录存在
os.makedirs(LOG_ROOT, exist_ok=True)
#日志级别error info debug
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    """构建并返回日志器。

    参数：
        name: 日志器名称。
        console_level: 控制台日志级别。
        file_level: 文件日志级别。
        log_file: 指定日志文件路径；为空时按日期自动命名。
    返回：
        已配置好的 logging.Logger 实例。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 防止同一 logger 被重复绑定 handler，导致日志重复打印。
    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger

#快捷获取日志器
logger = get_logger()

if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
