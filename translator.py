import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import acompletion
import json

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing in .env")
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat history", [])
    msg = cl.Message(content = "Welcome to the ****Translator Agent*******\n\n Please tell me **what you do you want to translate").send
    await msg.send()
    
@cl.on_message
async def on_message(message: cl.Message):
    msg1 = cl.Message(content ="Translating....")
    await msg1.send()
    
    history = cl.user_session.get("chat_history") or []
    history.append({"role":"user", "Content":message.content})
    try:
        response = await acompletion(
            medel = "gemini/gemini-1.5-flash",
            api_key = gemini_api_key,
            messages= history # type: ignore
        )
        response_content = response.choices[0].message.thinking_content
        msg1.content = response_content
        await msg1.update()
        history.append({"role":"assistant", "content": response_content}) # type: ignore
        cl.user_session.set("chat_history", history) # type: ignore
        
    except Exception as e:
        msg1.content = f"Error:{str(e)}"
        await msg1.update()
@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    
    with open("translation_chat_history.json", "w" ) as f:
        json.dump(history, f, indent = 2) 
        
    print("chat history saved")            
            

  