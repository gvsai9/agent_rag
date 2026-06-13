# utils/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_pipeline_logger(module_name: str = "pipeline") -> logging.Logger:
    """
    Sets up a file-only logger that silences console prints
    and records structured execution events safely to a local file.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicating handlers if this module is imported multiple times
    if logger.handlers:
        return logger

    # 1. Structure the layout: Timestamps, Log Levels, File Name, and Line Numbers
    log_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 2. File Handler with size caps to save disk space
    # Splits files seamlessly at 5MB boundaries and keeps up to 5 rolling backup rotations.
    file_handler = RotatingFileHandler(
        "pipeline_execution.log", 
        maxBytes=5 * 1024 * 1024, 
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger