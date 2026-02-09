"""
Mobile Channel Adapter (Future)
===============================

Placeholder for mobile app integration.
When mobile app is built, this adapter will:
- Handle push notification tokens
- Format responses for mobile UI
- Handle mobile-specific features

All AI logic remains in the Agent Gateway.
"""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UnifiedMessage:
    """Unified message format for all channels"""
    user_id: str
    message: str
    platform: str = "mobile"
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MobileAdapter:
    """
    Mobile Channel Adapter (Future)
    
    This class will:
    - Receive messages from mobile app
    - Handle push notifications
    - Format responses for mobile UI
    
    NO AI LOGIC HERE - just message routing.
    """
    
    def __init__(self, gateway=None):
        """
        Initialize Mobile adapter
        
        Args:
            gateway: Agent Gateway instance for processing messages
        """
        self.gateway = gateway
        self.platform = "mobile"
        self.push_tokens: dict = {}  # user_id -> push_token
        logger.info("📱 Mobile Adapter initialized (placeholder)")
    
    def set_gateway(self, gateway):
        """Set the Agent Gateway for message processing"""
        self.gateway = gateway
    
    def register_push_token(self, user_id: str, token: str, platform: str = "ios"):
        """
        Register push notification token for user
        
        Args:
            user_id: User ID
            token: Push notification token
            platform: ios or android
        """
        self.push_tokens[user_id] = {
            "token": token,
            "platform": platform
        }
        logger.info(f"Push token registered for user {user_id}")
    
    def to_unified_message(
        self,
        user_id: str,
        text: str,
        device_id: str = None,
        app_version: str = None
    ) -> UnifiedMessage:
        """
        Convert mobile request to unified format
        
        Args:
            user_id: User ID
            text: Message text
            device_id: Mobile device ID
            app_version: App version
            
        Returns:
            UnifiedMessage in standard format
        """
        return UnifiedMessage(
            user_id=f"mobile_{user_id}",
            message=text,
            platform=self.platform,
            metadata={
                "device_id": device_id,
                "app_version": app_version
            }
        )
    
    async def process_message(self, unified_msg: UnifiedMessage) -> str:
        """
        Send message to Agent Gateway and get response
        
        Args:
            unified_msg: Unified message format
            
        Returns:
            Response text from gateway
        """
        if not self.gateway:
            return "⚠️ Agent Gateway not configured"
        
        try:
            response = await self.gateway.process_message(
                user_id=unified_msg.user_id,
                message=unified_msg.message,
                platform=unified_msg.platform,
                metadata=unified_msg.metadata
            )
            return response.text
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            return "⚠️ Sorry, I encountered an error. Please try again."
    
    def format_response(self, text: str) -> dict:
        """
        Format response for mobile app
        
        Args:
            text: Response text
            
        Returns:
            Mobile-formatted response dict
        """
        return {
            "text": text,
            "platform": "mobile",
            "notification": {
                "title": "Sentri Security",
                "body": text[:100] if len(text) > 100 else text
            }
        }
    
    async def send_push_notification(self, user_id: str, title: str, body: str):
        """
        Send push notification to user (future implementation)
        
        Args:
            user_id: User to notify
            title: Notification title
            body: Notification body
        """
        if user_id not in self.push_tokens:
            logger.warning(f"No push token for user {user_id}")
            return False
        
        # Future: Implement actual push notification sending
        # via Firebase Cloud Messaging or Apple Push Notification Service
        logger.info(f"Push notification would be sent to {user_id}: {title}")
        return True
