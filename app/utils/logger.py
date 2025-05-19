"""
Logging configuration for KOL Sentiment MCP
"""
import os
import sys
from loguru import logger

def setup_logging():
    """Configure logging for the application"""
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    # Add file handler for logs
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_path, exist_ok=True)
    
    logger.add(
        os.path.join(log_path, "app.log"),
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    logger.info("Logging configured successfully")

def get_component_logger(component_name):
    """Get a logger for a specific component"""
    return logger.bind(name=component_name) 