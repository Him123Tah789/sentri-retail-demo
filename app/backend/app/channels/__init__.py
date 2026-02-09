# Channels Layer - Platform Adapters
# Each platform sends unified messages to the Agent Gateway

from .telegram.handler import TelegramAdapter
from .web.websocket import WebAdapter

__all__ = ["TelegramAdapter", "WebAdapter"]
