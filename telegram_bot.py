import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from graph import app, session_manager
from logger_config import setup_logger

logger = setup_logger("telegram_bot")

# Telegram Bot Token
TELEGRAM_TOKEN = "7856418853:AAGUh7pLJfd_AHQk5b3GXEyWNCcQ3LlF84E"

async def handle_new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts a new chat session."""
    user_id = update.effective_user.id
    session_id = session_manager.new_session(user_id)
    context.user_data["session_id"] = session_id
    logger.info(f"User {user_id} started new session {session_id}")
    await update.message.reply_text("Started a new chat session.")

async def handle_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sessions = session_manager.list_sessions(user_id)
    keyboard = [
        [InlineKeyboardButton(f"Session {sid[:8]}...", callback_data=f"session_{sid}")]
        for sid in sessions
    ]
    keyboard.append([InlineKeyboardButton("➕ New Chat", callback_data="session_new")])
    
    reply_text = "Select a session to continue or start a new one:"
    if not sessions:
        reply_text = "No previous sessions found. Start a new one?"

    await update.message.reply_text(
        reply_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data == "session_new":
        user_id = update.effective_user.id
        session_id = session_manager.new_session(user_id)
        context.user_data["session_id"] = session_id
        logger.info(f"User {user_id} started new session {session_id} via button.")
        await query.edit_message_text("Started new chat session.")
        return

    sid = callback_data.split("_", 1)[1]
    context.user_data["session_id"] = sid
    await query.edit_message_text(f"Switched to session {sid[:8]}...")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and sends them to the LangGraph app."""
    user_id = update.effective_user.id
    session_id = context.user_data.get("session_id")
    if not session_id:
        session_id = session_manager.new_session(user_id)
        context.user_data["session_id"] = session_id

    inputs = {"question": update.message.text}

    logger.info(f"Message from user {user_id}: {inputs['question'][:100]}...")
    
    try:
        result = app.invoke(inputs, session_id=session_id)
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
    application.add_handler(CommandHandler("new", handle_new_chat))
    application.add_handler(CommandHandler("chats", handle_chats))
    application.add_handler(CallbackQueryHandler(handle_session_callback, pattern="^session_"))
    
    logger.info("Bot is running and polling for messages...")
    application.run_polling()

if __name__ == "__main__":
    main()
    asyncio.run(main())
