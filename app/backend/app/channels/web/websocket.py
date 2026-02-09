"""
Web Channel Adapter
===================

This adapter handles web-based communication (REST API / WebSocket).
All AI logic is in the Agent Gateway.

Responsibilities:
- Receive web requests
- Convert to unified format
- Send to Agent Gateway
- Format response for web
"""

import logging
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class UnifiedMessage:
    """Unified message format for all channels"""
    user_id: str
    message: str
    platform: str = "web"
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class WebResponse:
    """Web-specific response format"""
    text: str
    intent: str = None
    confidence: float = None
    actions: list = None
    scan_result: dict = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
    
    def to_dict(self):
        return asdict(self)


class WebAdapter:
    """
    Web Channel Adapter
    
    This class:
    - Receives messages from web API
    - Converts them to unified format
    - Sends to Agent Gateway
    - Returns formatted response for web
    
    NO AI LOGIC HERE - just message routing.
    """
    
    def __init__(self, gateway=None):
        """
        Initialize Web adapter
        
        Args:
            gateway: Agent Gateway instance for processing messages
        """
        self.gateway = gateway
        self.platform = "web"
        logger.info("🌐 Web Adapter initialized")
    
    def set_gateway(self, gateway):
        """Set the Agent Gateway for message processing"""
        self.gateway = gateway
    
    def to_unified_message(
        self,
        user_id: str,
        text: str,
        session_id: str = None,
        ip_address: str = None
    ) -> UnifiedMessage:
        """
        Convert web request to unified format
        
        Args:
            user_id: User ID (from auth token)
            text: Message text
            session_id: Web session ID
            ip_address: Client IP address
            
        Returns:
            UnifiedMessage in standard format
        """
        return UnifiedMessage(
            user_id=f"web_{user_id}",
            message=text,
            platform=self.platform,
            metadata={
                "session_id": session_id,
                "ip_address": ip_address
            }
        )
    
    async def process_message(self, unified_msg: UnifiedMessage) -> WebResponse:
        """
        Send message to Agent Gateway and get response
        
        Args:
            unified_msg: Unified message format
            
        Returns:
            WebResponse with formatted data
        """
        if not self.gateway:
            return WebResponse(
                text="⚠️ Agent Gateway not configured",
                intent="error"
            )
        
        try:
            response = await self.gateway.process_message(
                user_id=unified_msg.user_id,
                message=unified_msg.message,
                platform=unified_msg.platform,
                metadata=unified_msg.metadata
            )
            
            return WebResponse(
                text=response.text,
                intent=response.intent.value if response.intent else None,
                confidence=response.confidence,
                actions=response.suggested_actions,
                scan_result=response.metadata.get("scan_result") if response.metadata else None
            )
            
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            return WebResponse(
                text="⚠️ Sorry, I encountered an error. Please try again.",
                intent="error"
            )
    
    def format_response(self, response: WebResponse) -> dict:
        """
        Format response for web API
        
        Args:
            response: WebResponse object
            
        Returns:
            Dict suitable for JSON response
        """
        return response.to_dict()
    
    # ==========================================
    # REST API Handler Methods
    # ==========================================
    
    async def handle_chat(
        self,
        user_id: str,
        message: str,
        session_id: str = None
    ) -> dict:
        """
        Handle chat message from web API
        
        Args:
            user_id: Authenticated user ID
            message: Message text
            session_id: Optional session ID
            
        Returns:
            Formatted response dict
        """
        unified_msg = self.to_unified_message(
            user_id=user_id,
            text=message,
            session_id=session_id
        )
        
        response = await self.process_message(unified_msg)
        return self.format_response(response)
    
    async def handle_scan(
        self,
        user_id: str,
        content: str,
        scan_type: str = "auto"
    ) -> dict:
        """
        Handle scan request from web API
        
        Args:
            user_id: Authenticated user ID
            content: Content to scan (URL, email, logs)
            scan_type: Type of scan (link, email, logs, auto)
            
        Returns:
            Formatted response dict
        """
        # Construct scan request message
        if scan_type == "link":
            message = f"Scan this link: {content}"
        elif scan_type == "email":
            message = f"Scan this email:\n{content}"
        elif scan_type == "logs":
            message = f"Scan these logs:\n{content}"
        else:
            message = content
        
        unified_msg = self.to_unified_message(
            user_id=user_id,
            text=message
        )
        
        response = await self.process_message(unified_msg)
        return self.format_response(response)


# ==========================================
# WebSocket Support (Future)
# ==========================================

class WebSocketManager:
    """
    WebSocket connection manager for real-time communication
    
    Future implementation for:
    - Real-time chat
    - Live security alerts
    - Streaming scan results
    """
    
    def __init__(self):
        self.active_connections: dict = {}
        logger.info("🔌 WebSocket Manager initialized")
    
    async def connect(self, websocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected: {user_id}")
    
    def disconnect(self, user_id: str):
        """Handle WebSocket disconnect"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected: {user_id}")
    
    async def send_message(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for connection in self.active_connections.values():
            await connection.send_json(message)
