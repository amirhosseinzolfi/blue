import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from graph import app
from logger_config import setup_logger

logger = setup_logger("telegram_bot")

# Telegram Bot Token
TELEGRAM_TOKEN = "7856418853:AAGUh7pLJfd_AHQk5b3GXEyWNCcQ3LlF84E"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and sends them to the LangGraph app."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"Message from user {user_id}: {user_message[:100]}...")
    
    inputs = {"question": user_message}

    try:
        result = app.invoke(inputs)
        response = result.get('answer', 'Sorry, I could not generate a response.')
        
        await update.message.reply_text(response)
        logger.info(f"Response sent to user {user_id}: {response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {e}")
        await update.message.reply_text("Sorry, there was an error processing your message.")

def main():
    """Starts the Telegram bot."""
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running and polling for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
    asyncio.run(main())
