import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import acompletion  # Changed to async version
import json

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing in .env")

@cl.on_chat_start
async def on_chat_start():
    # Initialize chat history
    cl.user_session.set("chat_history", [])
    
    # Create and send welcome message
    welcome_msg = cl.Message(
        content="Welcome to the ****Translator Agent*******\n\n"
                "Please tell me what you want to translate"
    )
    await welcome_msg.send()  # Fixed: Proper async send

@cl.on_message
async def on_message(message: cl.Message):
    # Create processing message
    processing_msg = cl.Message(content="Translating....")
    await processing_msg.send()
    
    # Get chat history
    history = cl.user_session.get("chat_history") or []
    
    # Add user message to history
    history.append({"role": "user", "content": message.content})
    
    try:
        # Make async API call
        response = await acompletion(  # Fixed: await + async version
            model="gemini/gemini-1.5-flash",  # Fixed: model spelling
            api_key=gemini_api_key,
            messages=history
        )
        
        # Get response content
        response_content = response.choices[0].message.content  # Fixed: correct property
        
        # Update processing message with translation
        processing_msg.content = response_content
        await processing_msg.update()
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)
        
    except Exception as e:
        processing_msg.content = f"Error: {str(e)}"
        await processing_msg.update()

@cl.on_chat_end
async def on_chat_end():
    # Get history and save to file
    history = cl.user_session.get("chat_history") or []  # Fixed: correct variable name
    
    with open("translation_chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print("Chat history saved")