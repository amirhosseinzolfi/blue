"""
Backend Core - AI Agent with LangGraph and Memory Management
Enhanced version of the provided LangGraph sample with tools support
"""

import os
import uuid
from typing import Annotated, Literal, List, Optional, Dict, Any
import operator
from datetime import datetime

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, RemoveMessage
)
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_core.tools import BaseTool, tool
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.pregel import Pregel
from langgraph.prebuilt import ToolNode

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

# --- Configuration ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://141.98.210.15:15203/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "deepseek-r1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "324")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))

OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

# --- Constants for Summarization ---
MESSAGES_TO_KEEP_AFTER_SUMMARY = int(os.getenv("MESSAGES_TO_KEEP_AFTER_SUMMARY", "2"))
NEW_MESSAGES_THRESHOLD_FOR_SUMMARY = int(os.getenv("NEW_MESSAGES_THRESHOLD_FOR_SUMMARY", "10"))

# --- Helper to ensure message has an ID ---
def ensure_message_has_id(message: BaseMessage) -> BaseMessage:
    if not hasattr(message, 'id') or message.id is None or not isinstance(message.id, str):
        new_id = str(uuid.uuid4())
        message.id = new_id
    return message

# --- Initialize LLM & Embeddings ---
llm = ChatOpenAI(
    base_url=LLM_BASE_URL, 
    model_name=LLM_MODEL_NAME, 
    temperature=LLM_TEMPERATURE, 
    api_key=LLM_API_KEY
)

try:
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    print(f"✓ OllamaEmbeddings initialized with model: {OLLAMA_EMBEDDING_MODEL}")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize OllamaEmbeddings: {e}")
    embeddings = None

# --- Define Tools ---
@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """Safely calculate mathematical expressions."""
    try:
        # Simple eval with basic safety checks
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Error: Invalid characters in expression"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def search_memory(query: str) -> str:
    """Search through conversation memory for relevant information."""
    # This is a placeholder - in a real implementation, you'd use vector search
    return f"Memory search results for '{query}': No relevant memories found yet."

# Available tools
tools = [get_current_time, calculate, search_memory]
tool_node = ToolNode(tools)

# Create tool-calling LLM
llm_with_tools = llm.bind_tools(tools)

# --- Define Enhanced Graph State ---
class AgentState(MessagesState):
    summary: str
    messages_since_last_summary: Annotated[int, operator.add]
    tools_used: List[str]
    session_id: str
    user_preferences: Dict[str, Any]

# --- Tool Calling Function ---
def should_continue(state: AgentState) -> Literal["tools", "should_summarize_node"]:
    """Determine if we should use tools or check for summarization."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, we continue to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise we check if we should summarize
    return "should_summarize_node"

# --- Define Enhanced Nodes ---
def call_llm_node(state: AgentState) -> dict:
    print("--- Node: call_llm_node ---")
    current_messages_in_state = state['messages']
    summary = state.get("summary", "")
    session_id = state.get("session_id", "default")
    
    messages_to_send_to_llm = []
    
    # Add system prompt with context
    system_prompt = """You are a helpful AI assistant with access to tools. You can:
    1. Get current time and date
    2. Perform mathematical calculations
    3. Search through conversation memory
    
    Use tools when appropriate to help the user. Be conversational and helpful.
    """
    
    if summary:
        system_prompt += f"\n\nConversation summary so far: {summary}"
    
    messages_to_send_to_llm.append(ensure_message_has_id(SystemMessage(content=system_prompt)))
    
    # Add conversation history
    for msg in current_messages_in_state:
        if not isinstance(msg, RemoveMessage):
            messages_to_send_to_llm.append(msg)

    if not any(isinstance(m, (HumanMessage, SystemMessage)) for m in messages_to_send_to_llm):
        messages_to_send_to_llm.append(ensure_message_has_id(HumanMessage(content="Hello.")))

    response = llm_with_tools.invoke(messages_to_send_to_llm)
    
    # Track tools used
    tools_used = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tools_used = [tool_call['name'] for tool_call in response.tool_calls]
    
    return {
        "messages": [ensure_message_has_id(response)], 
        "messages_since_last_summary": 1,
        "tools_used": tools_used
    }

def should_summarize_node(state: AgentState) -> dict:
    print("--- Node: should_summarize_node ---")
    num_since_last_summary = state.get("messages_since_last_summary", 0)
    
    print(f"Messages since last summary: {num_since_last_summary}")
    if num_since_last_summary >= NEW_MESSAGES_THRESHOLD_FOR_SUMMARY:
        print(f"Condition met for summarization: {num_since_last_summary} new messages >= {NEW_MESSAGES_THRESHOLD_FOR_SUMMARY}")
        # Return empty dict - the conditional edge will handle routing to summarization
        return {}
    else:
        print(f"Condition not met ({num_since_last_summary} new messages). Ending turn.")
        # Return empty dict - the conditional edge will handle routing to END
        return {}

def summarize_conversation_node(state: AgentState):
    print("--- Node: summarize_conversation_node ---")
    current_messages_in_state = state['messages']
    
    # Messages to summarize
    messages_to_summarize_content_from = [
        m for m in current_messages_in_state if isinstance(m, (HumanMessage, AIMessage, SystemMessage))
    ]
    
    existing_summary = state.get("summary", "")
    prompt_header = ("Please extend this summary with the new conversation excerpts below. The existing summary captures the essence of discussions prior to these new excerpts. Focus on integrating the new information seamlessly.\n" 
                     if existing_summary 
                     else "Please create a concise summary of the following conversation, capturing the key points discussed:\n")
            
    formatted_messages_for_summary_prompt = []
    for msg in messages_to_summarize_content_from:
        if isinstance(msg, HumanMessage): 
            formatted_messages_for_summary_prompt.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage): 
            formatted_messages_for_summary_prompt.append(f"AI: {msg.content}")
        elif isinstance(msg, SystemMessage): 
            formatted_messages_for_summary_prompt.append(f"System: {msg.content}")
            
    full_summarization_prompt_text = prompt_header 
    if existing_summary:
        full_summarization_prompt_text += f"\nPrevious Summary:\n{existing_summary}\n\nNew Excerpts to Incorporate:\n"
    full_summarization_prompt_text += "\n".join(formatted_messages_for_summary_prompt)

    print(f"DEBUG: Summarization prompt (first 300): {full_summarization_prompt_text[:300]}...")
    summary_llm_response = llm.invoke([ensure_message_has_id(HumanMessage(content=full_summarization_prompt_text))])
    new_summary = summary_llm_response.content.strip()
    print(f"Generated new summary: '{new_summary[:100]}...'")

    # Create removal directives
    delete_directives = []
    num_to_remove_from_this_block = len(messages_to_summarize_content_from) - MESSAGES_TO_KEEP_AFTER_SUMMARY
    
    if num_to_remove_from_this_block > 0:
        messages_to_physically_remove = messages_to_summarize_content_from[:num_to_remove_from_this_block]
        for m_to_remove in messages_to_physically_remove:
            if hasattr(m_to_remove, 'id') and m_to_remove.id is not None and isinstance(m_to_remove.id, str):
                delete_directives.append(RemoveMessage(id=m_to_remove.id))
            else:
                print(f"Critical Warning: Summarized message type {type(m_to_remove)} content '{m_to_remove.content[:20]}' lacks valid ID for removal.")

        print(f"Creating RemoveMessage directives for {len(delete_directives)} messages from the current summarization block.")
    else:
        print("Not enough messages in the current summarization block to prune, or keeping all of them.")

    current_msg_since_last_summary = state.get("messages_since_last_summary", 0)
    return {
        "summary": new_summary,
        "messages": delete_directives,
        "messages_since_last_summary": MESSAGES_TO_KEEP_AFTER_SUMMARY - current_msg_since_last_summary
    }

def should_summarize_router(state: AgentState) -> Literal["summarize_conversation_node", "__end__"]:
    """Router function to determine if we should summarize or end"""
    num_since_last_summary = state.get("messages_since_last_summary", 0)
    
    if num_since_last_summary >= NEW_MESSAGES_THRESHOLD_FOR_SUMMARY:
        return "summarize_conversation_node"
    else:
        return "__end__"

# --- Define Graph ---
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("llm_caller", call_llm_node)
workflow.add_node("tools", tool_node)
workflow.add_node("summarize_conversation_node", summarize_conversation_node)

# Set entry point
workflow.set_entry_point("llm_caller")

# Add conditional edges
workflow.add_conditional_edges(
    "llm_caller",
    should_continue,
    {"tools": "tools", "should_summarize_node": "should_summarize_node"}
)

workflow.add_edge("tools", "llm_caller")

# Add summarization nodes and edges
workflow.add_node("should_summarize_node", should_summarize_node)
workflow.add_conditional_edges(
    "should_summarize_node",
    should_summarize_router,  # Use the separate router function
    {"summarize_conversation_node": "summarize_conversation_node", "__end__": END}
)
workflow.add_edge("summarize_conversation_node", END)

# --- Chat Interface Functions ---
class ChatbotBackend:
    def __init__(self, db_path: str = "./data/chatbot_messages.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Use direct SQLite connection with thread safety like in the example
        import sqlite3
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(self.conn)
        self.app = workflow.compile(checkpointer=self.checkpointer)
        
        print(f"✓ Chatbot backend initialized with SQLite persistence: {db_path}")
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("✓ Database connection closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()
    
    def get_config(self, session_id: str) -> dict:
        """Get configuration for a session"""
        return {"configurable": {"thread_id": session_id}}
    
    def initialize_session(self, session_id: str, system_prompt: str = None) -> bool:
        """Initialize a new chat session"""
        config = self.get_config(session_id)
        current_state_snapshot = self.app.get_state(config)
        
        is_new_conversation = True
        if current_state_snapshot and current_state_snapshot.values:
            if current_state_snapshot.values.get("messages"):
                is_new_conversation = False
        
        if is_new_conversation:
            if not system_prompt:
                system_prompt = "You are a helpful AI assistant with access to various tools. Be conversational and assist the user with their requests."
            
            initial_system_message = ensure_message_has_id(SystemMessage(content=system_prompt))
            initial_state_update = {
                "messages": [initial_system_message],
                "summary": "",
                "messages_since_last_summary": 0,
                "tools_used": [],
                "session_id": session_id,
                "user_preferences": {}
            }
            self.app.update_state(config, initial_state_update)
            return True
        return False
    
    def send_message(self, session_id: str, message: str) -> str:
        """Send a message and get response"""
        config = self.get_config(session_id)
        
        # Ensure session is initialized
        self.initialize_session(session_id)
        
        user_message_with_id = ensure_message_has_id(HumanMessage(content=message))
        inputs = {"messages": [user_message_with_id]}
        
        try:
            # Use invoke for consistent results like in the example
            result = self.app.invoke(inputs, config=config)
            
            # Get the last AI message from the result
            reply = ""
            for msg in reversed(result.get("messages", [])):
                if isinstance(msg, AIMessage):
                    reply = msg.content
                    break
            
            return reply if reply else "I apologize, but I couldn't process your request."
            
        except Exception as e:
            print(f"Error in send_message: {e}")
            return f"I encountered an error: {str(e)}"
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        config = self.get_config(session_id)
        current_state_snapshot = self.app.get_state(config)
        
        if not current_state_snapshot or not current_state_snapshot.values:
            return []
        
        messages = current_state_snapshot.values.get("messages", [])
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content, "timestamp": datetime.now().isoformat()})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content, "timestamp": datetime.now().isoformat()})
        
        return history
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        config = self.get_config(session_id)
        current_state_snapshot = self.app.get_state(config)
        
        if not current_state_snapshot or not current_state_snapshot.values:
            return {"session_id": session_id, "exists": False}
        
        values = current_state_snapshot.values
        return {
            "session_id": session_id,
            "exists": True,
            "summary": values.get("summary", ""),
            "messages_count": len(values.get("messages", [])),
            "messages_since_last_summary": values.get("messages_since_last_summary", 0),
            "tools_used": values.get("tools_used", []),
            "user_preferences": values.get("user_preferences", {})
        }
    
    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with their metadata"""
        try:
            # Get all threads from the checkpointer using existing connection
            sessions = []
            
            # Use the existing connection to query the database
            cursor = self.conn.cursor()
            
            # Get all unique thread_ids from the checkpoints table
            cursor.execute("""
                SELECT DISTINCT thread_id, MIN(checkpoint_ns) as first_checkpoint, MAX(checkpoint_ns) as last_checkpoint
                FROM checkpoints 
                GROUP BY thread_id
                ORDER BY last_checkpoint DESC
            """)
            
            for row in cursor.fetchall():
                thread_id, first_checkpoint, last_checkpoint = row
                
                # Get session info for each thread
                try:
                    session_info = self.get_session_info(thread_id)
                    if session_info.get("exists", False):
                        # Add timestamps
                        session_info["created_at"] = first_checkpoint
                        session_info["last_activity"] = last_checkpoint
                        
                        # Get a preview of the conversation
                        history = self.get_chat_history(thread_id)
                        if history:
                            # Get the first user message as title
                            user_messages = [msg for msg in history if msg["role"] == "user"]
                            if user_messages:
                                session_info["title"] = user_messages[0]["content"][:50] + "..." if len(user_messages[0]["content"]) > 50 else user_messages[0]["content"]
                            else:
                                session_info["title"] = "New Chat"
                        else:
                            session_info["title"] = "Empty Chat"
                        
                        sessions.append(session_info)
                        
                except Exception as e:
                    print(f"Error getting info for session {thread_id}: {e}")
                    continue
            
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its data"""
        try:
            # Use the existing connection to delete session data
            cursor = self.conn.cursor()
            
            # Delete all checkpoints for this thread_id
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (session_id,))
            cursor.execute("DELETE FROM writes WHERE thread_id = ?", (session_id,))
            
            self.conn.commit();
            
            print(f"Session {session_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def get_session_preview(self, session_id: str) -> Dict[str, Any]:
        """Get a preview of a session for listing purposes"""
        try:
            session_info = self.get_session_info(session_id)
            if not session_info.get("exists", False):
                return None
            
            # Get recent history for preview
            history = self.get_chat_history(session_id)
            
            # Create preview
            preview = {
                "session_id": session_id,
                "title": "New Chat",
                "last_message": "",
                "message_count": len(history),
                "summary": session_info.get("summary", ""),
                "created_at": None,  # Would need to be tracked separately
                "last_activity": None  # Would need to be tracked separately
            }
            
            if history:
                # Get title from first user message
                user_messages = [msg for msg in history if msg["role"] == "user"]
                if user_messages:
                    preview["title"] = user_messages[0]["content"][:50] + "..." if len(user_messages[0]["content"]) > 50 else user_messages[0]["content"]
                
                # Get last message
                if history:
                    last_msg = history[-1]
                    preview["last_message"] = last_msg["content"][:100] + "..." if len(last_msg["content"]) > 100 else last_msg["content"]
                    preview["last_activity"] = last_msg.get("timestamp")
            
            return preview
            
        except Exception as e:
            print(f"Error getting session preview for {session_id}: {e}")
            return None

# --- Command Line Interface ---
def run_terminal_chat(backend: ChatbotBackend):
    """Run chat interface in terminal"""
    print("🤖 AI Chatbot Terminal Interface")
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("Type '/new' to start a new session")
    print("Type '/history' to see chat history")
    print("Type '/info' to see session info")
    print("-" * 50)
    
    session_id = f"terminal_{uuid.uuid4().hex[:8]}"
    backend.initialize_session(session_id, "You are a helpful AI assistant with access to tools. Be conversational and help the user with their requests.")
    
    print(f"Session ID: {session_id}")
    print("Bot: Hello! How can I help you today?")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Bot: Goodbye! Have a great day!")
                break
            
            if user_input == "/new":
                session_id = f"terminal_{uuid.uuid4().hex[:8]}"
                backend.initialize_session(session_id)
                print(f"New session started: {session_id}")
                print("Bot: Hello! How can I help you today?")
                continue
            
            if user_input == "/history":
                history = backend.get_chat_history(session_id)
                print("\n--- Chat History ---")
                for entry in history[-10:]:  # Show last 10 messages
                    print(f"{entry['role'].title()}: {entry['content']}")
                print("--- End History ---\n")
                continue
                
            if user_input == "/info":
                info = backend.get_session_info(session_id)
                print(f"\n--- Session Info ---")
                for key, value in info.items():
                    print(f"{key}: {value}")
                print("--- End Info ---\n")
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
    # Initialize backend
    backend = ChatbotBackend()
    
    # Run terminal interface
    run_terminal_chat(backend)
