"""
Simple logging configuration
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure basic logging"""
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    return logging.getLogger("sentri")


# Create default logger
logger = setup_logging()