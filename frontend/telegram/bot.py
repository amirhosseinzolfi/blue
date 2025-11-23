"""
Telegram Bot Frontend for AI Chatbot
Connects to the LangGraph backend via API
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackContext,
    filters
)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from simple_core import SimpleChatbotBackend

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize chatbot backend
chatbot_backend = SimpleChatbotBackend()

# Store user sessions
user_sessions: Dict[int, str] = {}

class TelegramChatbot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("new", self.new_session_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("info", self.info_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Telegram bot initialized")
    
    async def start_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or f"user_{user_id}"
        
        # Create session for user
        session_id = f"telegram_{user_id}_{username}"
        user_sessions[user_id] = session_id
        
        # Initialize backend session
        system_prompt = f"""You are a helpful AI assistant talking to {username} via Telegram.
You have access to various tools and can help with calculations, provide current time, and search conversation history.
Be conversational, concise (suitable for Telegram), and helpful. Use tools when appropriate."""
        
        chatbot_backend.initialize_session(session_id, system_prompt)
        
        welcome_message = f"""🤖 **Welcome to AI Chatbot!**

Hello {username}! I'm your AI assistant powered by LangGraph.

**What I can do:**
💬 Have natural conversations
🧮 Perform calculations  
🕐 Provide current time and date
🔍 Search through our conversation history
📝 Remember our conversation context

**Commands:**
/help - Show this help message
/new - Start a new conversation
/history - Show recent chat history
/info - Show session information

Your session: `{session_id}`

How can I help you today?"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /help command"""
        help_text = """🤖 **AI Chatbot Help**

**Available Commands:**
/start - Start chatting with the bot
/help - Show this help message
/new - Start a new conversation session
/history - Show your recent chat history
/info - Show your session information

**What I can do:**
💬 Have natural conversations
🧮 Perform mathematical calculations
🕐 Get current time and date
🔍 Search through conversation history
📝 Remember context across our conversation

**Tips:**
- Just send me any message to start chatting
- I can help with calculations like "What's 15 * 23?"
- Ask me "What time is it?" for current time
- I remember our conversation history

Need help with something specific? Just ask!"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def new_session_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /new command - start new session"""
        user_id = update.effective_user.id
        username = update.effective_user.username or f"user_{user_id}"
        
        # Create new session
        session_id = f"telegram_{user_id}_{username}_{os.urandom(4).hex()}"
        user_sessions[user_id] = session_id
        
        # Initialize new backend session
        system_prompt = f"""You are a helpful AI assistant talking to {username} via Telegram.
You have access to various tools and can help with calculations, provide current time, and search conversation history.
Be conversational, concise (suitable for Telegram), and helpful. Use tools when appropriate."""
        
        chatbot_backend.initialize_session(session_id, system_prompt)
        
        await update.message.reply_text(
            f"🔄 **New session started!**\n\nSession ID: `{session_id}`\n\nHow can I help you?",
            parse_mode='Markdown'
        )
    
    async def history_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /history command"""
        user_id = update.effective_user.id
        
        if user_id not in user_sessions:
            await update.message.reply_text("❌ No active session. Use /start to begin.")
            return
        
        session_id = user_sessions[user_id]
        
        try:
            history = chatbot_backend.get_chat_history(session_id)
            
            if not history:
                await update.message.reply_text("📝 No chat history yet. Start a conversation!")
                return
            
            # Format recent history
            history_text = "📋 **Recent Chat History:**\n\n"
            recent_messages = history[-10:]  # Last 10 messages
            
            for msg in recent_messages:
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                history_text += f"{role_icon} {content}\n\n"
            
            await update.message.reply_text(history_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting history: {str(e)}")
    
    async def info_command(self, update: Update, context: CallbackContext) -> None:
        """Handle /info command"""
        user_id = update.effective_user.id
        
        if user_id not in user_sessions:
            await update.message.reply_text("❌ No active session. Use /start to begin.")
            return
        
        session_id = user_sessions[user_id]
        
        try:
            info = chatbot_backend.get_session_info(session_id)
            
            info_text = f"""📊 **Session Information:**

**Session ID:** `{info['session_id']}`
**Status:** {'Active' if info['exists'] else 'Inactive'}
**Total Messages:** {info.get('messages_count', 0)}
**Since Last Summary:** {info.get('messages_since_last_summary', 0)}
**Tools Used:** {', '.join(info.get('tools_used', []) or ['None'])}

**Summary:** {info.get('summary', 'No summary yet')[:200]}{'...' if len(info.get('summary', '')) > 200 else ''}"""
            
            await update.message.reply_text(info_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting session info: {str(e)}")
    
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """Handle regular text messages"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # Check if user has a session
        if user_id not in user_sessions:
            await update.message.reply_text("❌ No active session. Use /start to begin chatting!")
            return
        
        session_id = user_sessions[user_id]
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get response from backend
            response = chatbot_backend.send_message(session_id, user_message)
            
            # Send response (split if too long for Telegram)
            if len(response) > 4096:
                # Split long messages
                for i in range(0, len(response), 4096):
                    await update.message.reply_text(response[i:i+4096])
            else:
                await update.message.reply_text(response)
            
        except Exception as e:
            error_message = f"❌ I encountered an error: {str(e)}"
            await update.message.reply_text(error_message)
            logger.error(f"Error handling message for user {user_id}: {e}")
    
    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.message:
            await update.message.reply_text("❌ An unexpected error occurred. Please try again.")
    
    async def setup_commands(self):
        """Set up bot commands for Telegram menu"""
        commands = [
            BotCommand("start", "Start chatting with the AI bot"),
            BotCommand("help", "Show help information"),
            BotCommand("new", "Start a new conversation"),
            BotCommand("history", "Show recent chat history"),
            BotCommand("info", "Show session information"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set up")
    
    async def run(self):
        """Run the bot"""
        # Set up error handler
        self.application.add_error_handler(self.error_handler)
        
        # Set up commands
        await self.setup_commands()
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot is running...")
        
        # Keep running - use a simple while loop instead of idle()
        try:
            import signal
            import asyncio
            
            # Create a future that will be set when we receive SIGINT or SIGTERM
            stop_future = asyncio.Future()
            
            def signal_handler():
                stop_future.set_result(None)
            
            # Register signal handlers
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
            
            # Wait for stop signal
            await stop_future
            
        except KeyboardInterrupt:
            logger.info("Bot stopping...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

async def main():
    """Main function to run the Telegram bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please set TELEGRAM_BOT_TOKEN in config/.env file")
        return
    
    print(f"🚀 Starting Telegram bot...")
    print(f"🤖 Bot token: {token[:10]}...")
    
    bot = TelegramChatbot(token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
