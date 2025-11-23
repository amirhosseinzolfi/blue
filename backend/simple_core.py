"""
Simplified Backend Core - No Streaming, Basic LangGraph
"""

import os
import uuid
from typing import Annotated, Literal, List, Optional, Dict, Any
import operator
from datetime import datetime

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

# Configuration
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://141.98.210.15:15203/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "deep-seek-r1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "324")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))

# Helper function
def ensure_message_has_id(message: BaseMessage) -> BaseMessage:
    if not hasattr(message, 'id') or message.id is None:
        message.id = str(uuid.uuid4())
    return message

# Initialize LLM
try:
    llm = ChatOpenAI(
        base_url=LLM_BASE_URL, 
        model_name=LLM_MODEL_NAME, 
        temperature=LLM_TEMPERATURE, 
        api_key=LLM_API_KEY
    )
    print(f"✅ LLM initialized: {LLM_MODEL_NAME}")
except Exception as e:
    print(f"⚠️ LLM initialization warning: {e}")
    # Use a mock LLM for testing
    class MockLLM:
        def invoke(self, messages):
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    self.id = str(uuid.uuid4())
            
            # Extract last human message
            last_human_msg = "Hello"
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    last_human_msg = msg.content
            
            # Generate appropriate response
            if any(word in last_human_msg.lower() for word in ["calculate", "math", "+", "-", "*", "/"]):
                return MockResponse("I can help with calculations! However, I'm currently in test mode. Try asking for the time instead.")
            elif "time" in last_human_msg.lower():
                return MockResponse(f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                return MockResponse(f"Hello! I received your message: '{last_human_msg}'. I'm currently running in test mode.")
    
    llm = MockLLM()

# Define tools
@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """Safely calculate mathematical expressions."""
    try:
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Error: Invalid characters in expression"
    except Exception as e:
        return f"Error: {str(e)}"

tools = [get_current_time, calculate]

# Simple State
class ChatState(MessagesState):
    pass

# Simple LLM node
def llm_node(state: ChatState):
    """Call LLM with current messages"""
    messages = state["messages"]
    
    # Add system message if needed
    system_prompt = """You are a helpful AI assistant with access to tools. You can:
    1. Get current time and date
    2. Perform mathematical calculations
    
    Be conversational and helpful. When users ask for calculations or time, let them know you have tools for that."""
    
    # Prepare messages for LLM
    formatted_messages = [SystemMessage(content=system_prompt)]
    formatted_messages.extend(messages)
    
    # Get response from LLM
    response = llm.invoke(formatted_messages)
    
    # Ensure response has ID
    if hasattr(response, 'content'):
        # It's already an AIMessage
        response = ensure_message_has_id(response)
    else:
        # Create AIMessage from response
        response = ensure_message_has_id(AIMessage(content=str(response)))
    
    return {"messages": [response]}

# Create workflow
workflow = StateGraph(ChatState)
workflow.add_node("llm", llm_node)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)

# Simplified Backend Class
class SimpleChatbotBackend:
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.app = workflow.compile(checkpointer=self.checkpointer)
        self.sessions = {}  # Track sessions
        print("✅ Simplified chatbot backend initialized")
    
    def get_config(self, session_id: str) -> dict:
        return {"configurable": {"thread_id": session_id}}
    
    def initialize_session(self, session_id: str, system_prompt: str = None) -> bool:
        """Initialize a new chat session"""
        config = self.get_config(session_id)
        
        # Check if session already exists
        try:
            current_state = self.app.get_state(config)
            if current_state and current_state.values.get("messages"):
                return False  # Session already exists
        except:
            pass  # New session
        
        # Initialize with system message
        if not system_prompt:
            system_prompt = "You are a helpful AI assistant with access to tools."
        
        initial_message = ensure_message_has_id(SystemMessage(content=system_prompt))
        self.app.update_state(config, {"messages": [initial_message]})
        self.sessions[session_id] = True
        
        return True
    
    def send_message(self, session_id: str, message: str) -> str:
        """Send a message and get response"""
        config = self.get_config(session_id)
        
        # Ensure session exists
        if session_id not in self.sessions:
            self.initialize_session(session_id)
        
        # Create user message
        user_message = ensure_message_has_id(HumanMessage(content=message))
        
        try:
            # Invoke the workflow (no streaming)
            result = self.app.invoke({"messages": [user_message]}, config=config)
            
            # Extract AI response
            if "messages" in result:
                ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
                if ai_messages:
                    return ai_messages[-1].content
            
            return "I couldn't process your request. Please try again."
            
        except Exception as e:
            print(f"Error in send_message: {e}")
            return f"I encountered an error: {str(e)}"
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        config = self.get_config(session_id)
        
        try:
            state = self.app.get_state(config)
            if not state or not state.values.get("messages"):
                return []
            
            messages = state.values["messages"]
            history = []
            
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({
                        "role": "user", 
                        "content": msg.content, 
                        "timestamp": datetime.now().isoformat()
                    })
                elif isinstance(msg, AIMessage):
                    history.append({
                        "role": "assistant", 
                        "content": msg.content, 
                        "timestamp": datetime.now().isoformat()
                    })
            
            return history
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        config = self.get_config(session_id)
        
        try:
            state = self.app.get_state(config)
            if not state or not state.values.get("messages"):
                return {"session_id": session_id, "exists": False}
            
            messages = state.values["messages"]
            return {
                "session_id": session_id,
                "exists": True,
                "summary": "No summary in simplified version",
                "messages_count": len(messages),
                "messages_since_last_summary": 0,
                "tools_used": [],
                "user_preferences": {}
            }
            
        except Exception as e:
            print(f"Error getting session info: {e}")
            return {"session_id": session_id, "exists": False}

# Terminal interface
def run_terminal_chat(backend: SimpleChatbotBackend):
    """Run chat interface in terminal"""
    print("🤖 AI Chatbot Terminal Interface (Simplified)")
    print("Type 'exit', 'quit', or 'bye' to end")
    print("Type '/new' to start a new session")
    print("-" * 50)
    
    session_id = f"terminal_{uuid.uuid4().hex[:8]}"
    backend.initialize_session(session_id)
    
    print(f"Session ID: {session_id}")
    print("Bot: Hello! How can I help you today?")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Bot: Goodbye!")
                break
            
            if user_input == "/new":
                session_id = f"terminal_{uuid.uuid4().hex[:8]}"
                backend.initialize_session(session_id)
                print(f"New session started: {session_id}")
                print("Bot: Hello! How can I help you today?")
                continue
            
            if not user_input:
                continue
            
            response = backend.send_message(session_id, user_input)
            print(f"Bot: {response}")
            
        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Test the simplified backend
    backend = SimpleChatbotBackend()
    run_terminal_chat(backend)
