"""
Chainlit Frontend for AI Chatbot
Enhanced with authentication, data persistence, and history management
"""

import chainlit as cl
import os
import sys
import uuid
from typing import Dict, Any, List, Optional
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from core import ChatbotBackend

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

# Initialize chatbot backend
chatbot_backend = ChatbotBackend()

# Global storage for user sessions
user_sessions: Dict[str, str] = {}
available_sessions: List[Dict[str, Any]] = []

async def load_available_sessions():
    """Load all available sessions from backend"""
    try:
        global available_sessions
        available_sessions = chatbot_backend.list_sessions()
        return available_sessions
    except Exception as e:
        print(f"Error loading sessions: {e}")
        return []

async def show_session_selector():
    """Show session selector with actions"""
    try:
        sessions = await load_available_sessions()
        
        if sessions:
            # Create session selection content
            session_content = "## 💬 Available Chat Sessions\n\n"
            session_content += f"**Total Sessions:** {len(sessions)}\n\n"
            
            for i, session in enumerate(sessions[:10]):  # Show max 10 sessions
                messages_count = session.get('messages_count', 0)
                preview = session.get('preview', 'No messages')
                session_id_short = session['session_id'][-12:]  # Show last 12 chars
                
                session_content += f"**{i+1}.** `{session_id_short}` ({messages_count} messages)\n"
                session_content += f"└ *{preview}*\n\n"
            
            session_content += "\n---\n\n"
            session_content += "**Quick Actions:**\n\n"
            session_content += "💡 *Click the buttons below to manage your sessions*\n"
            
            # Create actions for session management
            actions = [
                cl.Action(name="new_session", value="new", label="🆕 New Session"),
                cl.Action(name="refresh_sessions", value="refresh", label="🔄 Refresh List"),
            ]
            
            # Add switch actions for recent sessions (max 5)
            for i, session in enumerate(sessions[:5]):
                session_id_short = session['session_id'][-8:]
                actions.append(
                    cl.Action(
                        name="switch_session", 
                        value=session['session_id'], 
                        label=f"▶️ Switch to {session_id_short}"
                    )
                )
            
            await cl.Message(
                content=session_content,
                actions=actions
            ).send()
        else:
            # No sessions available
            no_sessions_content = "## 💬 Chat Sessions\n\n"
            no_sessions_content += "**No previous sessions found.**\n\n"
            no_sessions_content += "Start chatting to create your first session!\n\n"
            
            actions = [
                cl.Action(name="new_session", value="new", label="🆕 New Session"),
            ]
            
            await cl.Message(
                content=no_sessions_content,
                actions=actions
            ).send()
            
    except Exception as e:
        print(f"Error showing session selector: {e}")
        # Fallback message
        await cl.Message(
            content="⚠️ **Session Management Unavailable**\n\nContinue chatting in the current session.",
            actions=[cl.Action(name="new_session", value="new", label="🆕 New Session")]
        ).send()

@cl.action_callback("new_session")
async def on_new_session(action):
    """Handle new session creation"""
    # Create new session ID
    user = cl.user_session.get("user")
    user_id = user.identifier if user else f"guest_{uuid.uuid4().hex[:8]}"
    new_session_id = f"chainlit_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Store session ID
    cl.user_session.set("session_id", new_session_id)
    user_sessions[user_id] = new_session_id
    
    # Initialize backend session
    system_prompt = """You are a helpful AI assistant with access to various tools. 
You can help with calculations, provide current time, and search through our conversation history.
Be conversational, helpful, and engaging. Use tools when appropriate to provide better assistance."""
    
    chatbot_backend.initialize_session(new_session_id, system_prompt)
    
    await cl.Message(content=f"🆕 **New session created!**\n\nSession ID: `{new_session_id}`\n\nHow can I help you today?").send()
    await show_session_selector()

@cl.action_callback("refresh_sessions")
async def on_refresh_sessions(action):
    """Handle session list refresh"""
    await cl.Message(content="🔄 **Refreshing session list...**").send()
    await show_session_selector()

@cl.action_callback("switch_session")
async def on_switch_session(action):
    """Handle session switching"""
    target_session_id = action.value
    
    # Update current session
    cl.user_session.set("session_id", target_session_id)
    
    # Get session info and history
    session_info = chatbot_backend.get_session_info(target_session_id)
    history = chatbot_backend.get_chat_history(target_session_id)
    
    # Show session switch confirmation
    messages_count = session_info.get('messages_count', 0)
    summary = session_info.get('summary', 'No summary available')
    
    switch_message = f"🔄 **Switched to session:** `{target_session_id}`\n\n"
    switch_message += f"**Messages:** {messages_count}\n"
    
    if summary:
        switch_message += f"**Summary:** {summary[:200]}...\n\n"
    
    # Show recent messages for context
    if history:
        switch_message += "**Recent messages:**\n"
        recent_messages = history[-3:]  # Show last 3 messages
        for msg in recent_messages:
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            switch_message += f"{role_icon} {content_preview}\n"
    
    switch_message += "\n✨ Continue the conversation below!"
    
    await cl.Message(content=switch_message).send()
    await show_session_selector()

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session when user starts a conversation"""
    
    # Get user info (if authentication is enabled)
    user = cl.user_session.get("user")
    user_id = user.identifier if user else f"guest_{uuid.uuid4().hex[:8]}"
    
    # Create session ID
    session_id = f"chainlit_{user_id}_{uuid.uuid4().hex[:8]}"
    
    # Store session ID in user session
    cl.user_session.set("session_id", session_id)
    user_sessions[user_id] = session_id
    
    # Initialize backend session
    system_prompt = """You are a helpful AI assistant with access to various tools. 
You can help with calculations, provide current time, and search through our conversation history.
Be conversational, helpful, and engaging. Use tools when appropriate to provide better assistance."""
    
    chatbot_backend.initialize_session(session_id, system_prompt)
    
    # Send welcome message
    welcome_message = f"""# Welcome to AI Chatbot! 🤖

Hello! I'm your AI assistant powered by LangGraph and enhanced with tool capabilities.

**What I can do:**
- 💬 Have natural conversations
- 🧮 Perform calculations
- 🕐 Provide current time and date
- 🔍 Search through our conversation history
- 📝 Remember our conversation context

**Session Management:**
- 🆕 **Current Session:** `{session_id}`
- 💾 **Persistent Storage:** Your conversations are automatically saved
- 🔄 **Switch Sessions:** Use the action buttons or `/switch <session_id>`
- 📋 **View All Sessions:** Use the action buttons or `/sessions`

**Quick Commands:**
- `/new` - Start a new session
- `/sessions` - Show all your sessions  
- `/help` - Show all available commands

How can I help you today?"""
    
    await cl.Message(content=welcome_message).send()
    
    # Show session selector instead of chat history
    await show_session_selector()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    
    # Get session ID
    session_id = cl.user_session.get("session_id")
    if not session_id:
        await cl.Message(content="❌ Session not found. Please refresh the page.").send()
        return
    
    # Handle special commands
    if message.content.startswith('/'):
        await handle_command(message.content, session_id)
        return
    
    # Show typing indicator
    async with cl.Step(name="thinking") as step:
        step.input = message.content
        
        try:
            # Send message to backend
            response = chatbot_backend.send_message(session_id, message.content)
            step.output = response
            
        except Exception as e:
            response = f"❌ I encountered an error: {str(e)}"
            step.output = response
    
    # Send response
    await cl.Message(content=response).send()

async def handle_command(command: str, current_session_id: str):
    """Handle special commands"""
    command = command.strip()
    
    if command == "/new":
        await on_new_session(type('obj', (object,), {'value': 'new'})())
        
    elif command.startswith("/switch "):
        session_id = command[8:].strip()
        if session_id:
            # Find full session ID if partial provided
            sessions = await load_available_sessions()
            full_session_id = None
            
            for session in sessions:
                if session['session_id'].endswith(session_id) or session['session_id'] == session_id:
                    full_session_id = session['session_id']
                    break
            
            if full_session_id:
                action_obj = type('obj', (object,), {'value': full_session_id})()
                await on_switch_session(action_obj)
            else:
                await cl.Message(content=f"❌ Session not found: {session_id}").send()
        else:
            await cl.Message(content="❌ Please provide a session ID: `/switch <session_id>`").send()
            
    elif command == "/sessions" or command == "/list":
        await show_session_selector()
        
    elif command == "/help":
        help_text = """## 🆘 Available Commands

**Session Management:**
- `/new` - Create a new chat session
- `/switch <session_id>` - Switch to an existing session
- `/sessions` or `/list` - Show all available sessions

**Session Information:**
- `/help` - Show this help message

**Tips:**
- You can use the action buttons above for quick session management
- Session IDs can be shortened (use last 8 characters)
- All your conversations are automatically saved
"""
        await cl.Message(content=help_text).send()
        
    else:
        await cl.Message(content=f"❌ Unknown command: {command}\n\nType `/help` for available commands.").send()

async def show_chat_history(session_id: str):
    """Show chat history in sidebar"""
    try:
        # Get list of all sessions
        sessions = chatbot_backend.list_sessions()
        
        if not sessions:
            print(f"No previous sessions found")
            return
            
        # Create sidebar content for session management
        sidebar_content = "## 💬 Chat Sessions\n\n"
        
        current_session_highlighted = False
        for i, session in enumerate(sessions[:10]):  # Limit to 10 recent sessions
            session_id_short = session['session_id'][-8:]  # Show last 8 chars
            preview = session['preview'][:50] + "..." if len(session['preview']) > 50 else session['preview']
            
            if session['session_id'] == session_id:
                sidebar_content += f"**🔸 {session_id_short}** (Current)\n"
                sidebar_content += f"*{preview}*\n\n"
                current_session_highlighted = True
            else:
                sidebar_content += f"💭 {session_id_short}\n"
                sidebar_content += f"{preview}\n\n"
        
        sidebar_content += "\n---\n\n"
        sidebar_content += "💡 **Tips:**\n"
        sidebar_content += "- Start a new conversation to create a new session\n"
        sidebar_content += "- All conversations are automatically saved\n"
        sidebar_content += "- Use tools like calculator and time for enhanced assistance\n"
        
        print(f"Sidebar content prepared for session: {session_id}")
        print(f"Found {len(sessions)} total sessions")
        
        # Note: Chainlit sidebar implementation would go here
        # For now, we're printing the sidebar content
        # In future versions, this could be displayed as a proper sidebar
            
    except Exception as e:
        print(f"Error showing chat history: {e}")

@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates"""
    session_id = cl.user_session.get("session_id")
    if session_id:
        # Update user preferences in backend
        # This would require implementing preference updates in the backend
        await cl.Message(content="⚙️ Settings updated!").send()

@cl.on_stop
async def on_stop():
    """Handle chat stop"""
    session_id = cl.user_session.get("session_id")
    if session_id:
        print(f"Chat session ended: {session_id}")

# Authentication configuration (optional)
# Note: Authentication can be configured in chainlit.toml or via environment variables
# For password auth, you can use:
# [auth]
# type = "password"
# 
# For OAuth, you can configure providers in chainlit.toml
# This simple implementation works without authentication for now

# Configuration for Chainlit
if __name__ == "__main__":
    # Run with specific configuration
    port = int(os.getenv("CHAINLIT_PORT", "8000"))
    
    print(f"🚀 Starting Chainlit interface on port {port}")
    print(f"🌐 Access the chat at: http://localhost:{port}")
    
    # You can run this with: chainlit run frontend/chainlit/app.py --port 8000
