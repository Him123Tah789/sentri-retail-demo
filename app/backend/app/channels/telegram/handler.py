"""
Telegram Channel Adapter
========================

This adapter ONLY handles Telegram-specific communication.
All AI logic is in the Agent Gateway.

Responsibilities:
- Receive Telegram messages
- Convert to unified format
- Send to Agent Gateway
- Format response for Telegram
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


@dataclass
class UnifiedMessage:
    """Unified message format for all channels"""
    user_id: str
    message: str
    platform: str = "telegram"
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TelegramAdapter:
    """
    Telegram Channel Adapter
    
    This class:
    - Receives messages from Telegram
    - Converts them to unified format
    - Sends to Agent Gateway
    - Returns formatted response to Telegram
    
    NO AI LOGIC HERE - just message routing.
    """
    
    def __init__(self, gateway=None):
        """
        Initialize Telegram adapter
        
        Args:
            gateway: Agent Gateway instance for processing messages
        """
        self.gateway = gateway
        self.platform = "telegram"
        self.bot = None
        self.application = None
        logger.info("📱 Telegram Adapter initialized")
    
    def set_gateway(self, gateway):
        """Set the Agent Gateway for message processing"""
        self.gateway = gateway
    
    def to_unified_message(
        self,
        telegram_user_id: int,
        text: str,
        chat_id: int = None,
        username: str = None
    ) -> UnifiedMessage:
        """
        Convert Telegram message to unified format
        
        Args:
            telegram_user_id: Telegram user ID
            text: Message text
            chat_id: Telegram chat ID
            username: Telegram username
            
        Returns:
            UnifiedMessage in standard format
        """
        return UnifiedMessage(
            user_id=f"telegram_{telegram_user_id}",
            message=text,
            platform=self.platform,
            metadata={
                "telegram_user_id": telegram_user_id,
                "chat_id": chat_id,
                "username": username
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
    
    def format_response(self, text: str) -> str:
        """
        Format response for Telegram
        
        Telegram supports Markdown, so we can use formatting.
        
        Args:
            text: Response text
            
        Returns:
            Telegram-formatted text
        """
        # Basic formatting for Telegram
        # Could add more Telegram-specific formatting here
        return text
    
    # ==========================================
    # Telegram Bot Integration (python-telegram-bot)
    # ==========================================
    
    async def setup_bot(self):
        """Setup Telegram bot with handlers"""
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN not set")
            return False
        
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
            
            self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            
            # Register handlers
            self.application.add_handler(CommandHandler("start", self._handle_start))
            self.application.add_handler(CommandHandler("help", self._handle_help))
            self.application.add_handler(CommandHandler("status", self._handle_status))
            self.application.add_handler(CommandHandler("scan", self._handle_scan))
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self._handle_message
            ))
            
            logger.info("✅ Telegram bot configured")
            return True
            
        except ImportError:
            logger.warning("⚠️ python-telegram-bot not installed")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram bot setup error: {e}")
            return False
    
    async def _handle_start(self, update, context):
        """Handle /start command"""
        welcome = """🛡️ *Welcome to Sentri Security Bot!*

I'm your AI-powered retail security assistant. I can help you:

• 🔗 Scan suspicious links
• 📧 Analyze phishing emails  
• 📋 Review security logs
• 💬 Answer security questions

*Quick Commands:*
/scan <url> - Scan a link
/help - Show all commands
/status - Check system status

Or just send me any message!"""
        
        await update.message.reply_text(welcome, parse_mode="Markdown")
    
    async def _handle_help(self, update, context):
        """Handle /help command"""
        help_text = """🆘 *Sentri Help*

*Commands:*
• /start - Welcome message
• /scan <url> - Scan a URL for threats
• /status - System status
• /help - This help message

*What I can analyze:*
• Suspicious URLs and links
• Phishing email content
• Security log entries
• General security questions

Just paste any content and I'll analyze it!"""
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def _handle_status(self, update, context):
        """Handle /status command"""
        if self.gateway:
            status = await self.gateway.get_status()
            status_text = f"""🛡️ *Sentri Status*

• Gateway: ✅ Online
• Platform: Telegram
• User: {update.effective_user.id}

Ready to protect you!"""
        else:
            status_text = "⚠️ Gateway not available"
        
        await update.message.reply_text(status_text, parse_mode="Markdown")
    
    async def _handle_scan(self, update, context):
        """Handle /scan command"""
        if context.args:
            url = " ".join(context.args)
            unified_msg = self.to_unified_message(
                telegram_user_id=update.effective_user.id,
                text=f"Scan this link: {url}",
                chat_id=update.effective_chat.id,
                username=update.effective_user.username
            )
            response = await self.process_message(unified_msg)
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("Usage: /scan <url>")
    
    async def _handle_message(self, update, context):
        """Handle regular text messages"""
        unified_msg = self.to_unified_message(
            telegram_user_id=update.effective_user.id,
            text=update.message.text,
            chat_id=update.effective_chat.id,
            username=update.effective_user.username
        )
        
        response = await self.process_message(unified_msg)
        formatted = self.format_response(response)
        
        await update.message.reply_text(formatted, parse_mode="Markdown")
    
    async def start_polling(self):
        """Start the bot in polling mode"""
        if self.application:
            logger.info("🚀 Starting Telegram bot polling...")
            await self.application.run_polling()
