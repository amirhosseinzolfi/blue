import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from graph import app

# Telegram Bot Token
TELEGRAM_TOKEN = "7856418853:AAGUh7pLJfd_AHQk5b3GXEyWNCcQ3LlF84E"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and sends them to the LangGraph app."""
    user_message = update.message.text
    print(f"Received message: {user_message}")
    inputs = {"question": user_message}

    response = ""
    # We need to run the stream in a separate thread to avoid blocking the asyncio event loop
    loop = asyncio.get_event_loop()
    async for output in await loop.run_in_executor(None, app.astream, inputs):
        for key, value in output.items():
            response = value.get('answer')
            if response:
                print(f"Sending response: {response}")
                await update.message.reply_text(response)
                return

async def main():
    """Starts the Telegram bot."""
    print("Starting bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handle all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
