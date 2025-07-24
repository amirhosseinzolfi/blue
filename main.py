import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from graph import app
from logger_config import setup_logger
# Import auth module to register the callback
import auth
import os

@cl.data_layer
def get_data_layer():
    # Use SQLite for simplicity, can be changed to PostgreSQL
    return SQLAlchemyDataLayer(conninfo="sqlite+aiosqlite:///./chainlit.db")

logger = setup_logger("chainlit_app")

@cl.on_chat_start
async def on_chat_start():
    logger.info("Chat started")
    await cl.Message(content="Hello! How can I help you today?").send()

@cl.on_message
async def on_message(message: cl.Message):
    logger.info(f"Received message: {message.content[:100]}...")
    
    # Get conversation history from Chainlit's thread
    thread_id = cl.context.session.thread_id
    data_layer = get_data_layer()
    
    # Build history from previous messages in this thread
    history = []
    if thread_id:
        try:
            thread = await data_layer.get_thread(thread_id)
            if thread and hasattr(thread, 'steps'):
                for step in thread.steps:
                    if step.type == 'user_message':
                        history.append({"role": "user", "content": step.input})
                    elif step.type == 'assistant_message':
                        history.append({"role": "assistant", "content": step.output})
        except Exception as e:
            logger.warning(f"Could not load thread history: {e}")
    
    inputs = {
        "question": message.content,
        "history": history
    }
    
    msg = cl.Message(content="")
    final_answer = ""

    try:
        async for output in app.astream(inputs):
            for _, v in output.items():
                ans = v.get("answer")
                if ans:
                    final_answer = ans
                    await msg.stream_token(ans)
        
        await msg.send()
        logger.info(f"Response sent: {final_answer[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(content="Sorry, I encountered an error processing your request.").send()
