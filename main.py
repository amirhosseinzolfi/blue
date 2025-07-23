import chainlit as cl
from graph import app

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])

@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    inputs = {"question": message.content}
    
    msg = cl.Message(content="")
    result = ""
    async for output in app.astream(inputs):
        for key, value in output.items():
            result = value.get('answer')
            if result:
                await msg.stream_token(result)

    await msg.send()
    history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("history", history)
