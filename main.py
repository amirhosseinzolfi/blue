import chainlit as cl
from graph import app
from logger_config import setup_logger

logger = setup_logger("chainlit_app")

@cl.on_chat_start
async def on_chat_start():
    logger.info("New chat session started")
    cl.user_session.set("history", [])

@cl.on_message
async def on_message(message: cl.Message):
    logger.info(f"Received message: {message.content[:100]}...")
    
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    inputs = {"question": message.content}
    
    msg = cl.Message(content="")
    result = ""
    
    try:
        async for output in app.astream(inputs):
            for key, value in output.items():
                result = value.get('answer')
                if result:
                    await msg.stream_token(result)
        
        await msg.send()
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("history", history)
        
        logger.info(f"Response sent: {msg.content[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await msg.send()
