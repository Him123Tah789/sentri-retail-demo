"""
Core utilities package
"""
from .config import settings
from .logging import logger, setup_logging

# Import security functions lazily to avoid circular imports
# These will be imported on demand when used

__all__ = [
    'settings',
    'logger',
    'setup_logging',
]
__all__ = [
    "settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "verify_token",
    "authenticate_user",
    "get_current_user",
    "get_current_user_optional",
    "logger",
    "setup_logging",
]
