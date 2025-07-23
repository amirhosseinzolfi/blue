import chainlit as cl
from graph import app
from logger_config import setup_logger
import database as db
import uuid

logger = setup_logger("chainlit_app")

db.init_db()

@cl.on_chat_start
async def on_chat_start():
    session_id = str(uuid.uuid4())
    cl.user_session.set("session_id", session_id)
    logger.info(f"New chat session started with ID: {session_id}")

    # Allow the user to resume a previous session
    sessions = db.get_user_sessions("chainlit_user") # Assuming a single user for now
    if sessions:
        actions = [
            cl.Action(name=f"session_{s_id}", value=s_id, label=f"Resume session from {c_at}")
            for s_id, c_at in sessions
        ]
        await cl.Message(content="Or resume a previous session:", actions=actions).send()

@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.user_session.get("session_id")
    if not session_id:
        await on_chat_start() # Should not happen, but as a fallback
        session_id = cl.user_session.get("session_id")

    logger.info(f"Received message in session {session_id}: {message.content[:100]}...")
    
    history = db.get_chat_history(session_id)
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
        db.save_chat_history(session_id, "chainlit_user", history)
        
        logger.info(f"Response sent in session {session_id}: {msg.content[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing message in session {session_id}: {e}")
        await cl.Message(content="Sorry, there was an error processing your message.").send()

@cl.action_callback("resume_session")
async def on_resume_session(action: cl.Action):
    session_id = action.value
    cl.user_session.set("session_id", session_id)

    history = db.get_chat_history(session_id)

    for message in history:
        if message['role'] == 'user':
            await cl.Message(content=message['content'], author="User").send()
        else:
            await cl.Message(content=message['content'], author="Assistant").send()

    await cl.Message(content=f"Resumed session {session_id}").send()
