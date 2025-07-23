import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from graph import app
from logger_config import setup_logger
import database as db

logger = setup_logger("telegram_bot")

# Telegram Bot Token
TELEGRAM_TOKEN = "7856418853:AAGUh7pLJfd_AHQk5b3GXEyWNCcQ3LlF84E"

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts a new chat session or continues the last one."""
    user_id = str(update.effective_user.id)
    session_id = db.get_last_session_id(user_id)

    if not session_id:
        session_id = str(uuid.uuid4())
        db.save_chat_history(session_id, user_id, [])

    user_sessions[user_id] = session_id

    await update.message.reply_text("Welcome! Your new chat session has started. Use /chats to view previous sessions.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and sends them to the LangGraph app."""
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    if user_id not in user_sessions:
        await start(update, context)

    session_id = user_sessions[user_id]

    logger.info(f"Message from user {user_id} in session {session_id}: {user_message[:100]}...")

    history = db.get_chat_history(session_id)
    history.append({"role": "user", "content": user_message})
    
    inputs = {"question": user_message}

    try:
        result = app.invoke(inputs)
        response = result.get('answer', 'Sorry, I could not generate a response.')
        
        history.append({"role": "assistant", "content": response})
        db.save_chat_history(session_id, user_id, history)

        await update.message.reply_text(response)
        logger.info(f"Response sent to user {user_id}: {response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {e}")
        await update.message.reply_text("Sorry, there was an error processing your message.")

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays previous chat sessions for the user to choose from."""
    user_id = str(update.effective_user.id)
    sessions = db.get_user_sessions(user_id)

    if not sessions:
        await update.message.reply_text("No previous chats found.")
        return

    keyboard = []
    for session_id, created_at in sessions:
        keyboard.append([InlineKeyboardButton(f"Chat from {created_at}", callback_data=f"session_{session_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a chat to continue:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button presses for session selection."""
    query = update.callback_query
    await query.answer()

    session_id = query.data.split('_')[1]
    user_id = str(query.from_user.id)
    user_sessions[user_id] = session_id

    await query.edit_message_text(text=f"Switched to chat session {session_id}.")

def main():
    """Starts the Telegram bot."""
    db.init_db()
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chats", list_chats))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running and polling for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
