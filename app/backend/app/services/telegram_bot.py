"""
Sentri Telegram Bot - Fast Channel Integration
Connects Telegram to the Sentri Agent Gateway

Usage:
1. Create bot via @BotFather on Telegram
2. Get the bot token
3. Set TELEGRAM_BOT_TOKEN environment variable
4. Run: python -m app.services.telegram_bot
"""
import os
import asyncio
import logging
from typing import Optional
from datetime import datetime

# Check for telegram library
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot not installed. Run: pip install python-telegram-bot")

from .agent_gateway import gateway, AgentMessage, IntentType

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


class SentriTelegramBot:
    """
    Telegram bot that connects to the Sentri Agent Gateway.
    
    All messages are routed through the gateway for processing.
    The bot just handles Telegram-specific formatting.
    """
    
    def __init__(self, token: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot is required. Run: pip install python-telegram-bot")
        
        self.token = token
        self.application: Optional[Application] = None
        self.bot: Optional[Bot] = None
        logger.info("🤖 Sentri Telegram Bot initialized")
    
    def build(self) -> Application:
        """Build the Telegram application"""
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("scan", self.cmd_scan))
        
        # Handle all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("✅ Telegram bot handlers registered")
        return self.application
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🛡️ *Welcome to Sentri Security Bot!*

I'm your AI-powered retail security guardian.

*What I can do:*
🔗 Scan suspicious links for phishing
📧 Analyze emails for fraud/scams
📋 Check security logs for threats
💬 Answer cybersecurity questions

*Quick Start:*
• Send any URL to scan it
• Type `/scan email <text>` to analyze emails
• Ask me anything about security!

Type /help for all commands.
Stay safe! 🚀
"""
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown'
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = AgentMessage(
            text="help",
            user_id=str(update.effective_user.id),
            channel="telegram",
            metadata={"chat_id": update.effective_chat.id}
        )
        response = await gateway.process_message(message)
        
        # Convert to Telegram-friendly format
        text = response.text.replace("**", "*")  # Bold syntax
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        message = AgentMessage(
            text="status",
            user_id=str(update.effective_user.id),
            channel="telegram",
            metadata={"chat_id": update.effective_chat.id}
        )
        response = await gateway.process_message(message)
        text = response.text.replace("**", "*")
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def cmd_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command with arguments"""
        args = context.args
        if not args:
            await update.message.reply_text(
                "Usage:\n"
                "/scan <url> - Scan a link\n"
                "/scan email <text> - Analyze email content\n"
                "/scan log <text> - Analyze log entries"
            )
            return
        
        scan_text = " ".join(args)
        message = AgentMessage(
            text=f"scan {scan_text}",
            user_id=str(update.effective_user.id),
            channel="telegram",
            metadata={"chat_id": update.effective_chat.id}
        )
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        response = await gateway.process_message(message)
        text = self._format_for_telegram(response.text)
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message"""
        user_text = update.message.text
        user_id = str(update.effective_user.id)
        
        logger.info(f"📩 Telegram message from {user_id}: {user_text[:50]}...")
        
        # Create agent message
        message = AgentMessage(
            text=user_text,
            user_id=user_id,
            channel="telegram",
            metadata={
                "chat_id": update.effective_chat.id,
                "username": update.effective_user.username,
                "first_name": update.effective_user.first_name
            }
        )
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        # Process through gateway
        response = await gateway.process_message(message)
        
        # Format and send response
        text = self._format_for_telegram(response.text)
        
        # Add risk indicator for scans
        if response.risk_score is not None:
            if response.risk_score >= 60:
                text = "⚠️ *HIGH RISK DETECTED*\n\n" + text
            elif response.risk_score >= 30:
                text = "⚡ *Potential Risk*\n\n" + text
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
        logger.info(f"📤 Sent response (intent: {response.intent.value}, tool: {response.tool_used})")
    
    def _format_for_telegram(self, text: str) -> str:
        """Convert markdown to Telegram-friendly format"""
        # Replace ** with * for bold (Telegram uses single *)
        text = text.replace("**", "*")
        
        # Escape special characters in non-code sections
        # But preserve code blocks
        
        return text
    
    def run(self):
        """Run the bot (blocking)"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
            return
        
        self.build()
        logger.info("🚀 Starting Sentri Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_async(self):
        """Run the bot asynchronously"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
            return
        
        self.build()
        logger.info("🚀 Starting Sentri Telegram Bot (async)...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)


# Singleton instance
_bot_instance: Optional[SentriTelegramBot] = None


def get_telegram_bot() -> Optional[SentriTelegramBot]:
    """Get or create the telegram bot instance"""
    global _bot_instance
    
    if not TELEGRAM_AVAILABLE:
        logger.warning("Telegram bot not available - library not installed")
        return None
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.warning("Telegram bot not available - TELEGRAM_BOT_TOKEN not set")
        return None
    
    if _bot_instance is None:
        _bot_instance = SentriTelegramBot(token)
    
    return _bot_instance


def run_telegram_bot():
    """Run telegram bot standalone"""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        print("   Get a token from @BotFather on Telegram")
        return
    
    bot = SentriTelegramBot(token)
    bot.run()


# Allow running as script
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_telegram_bot()
