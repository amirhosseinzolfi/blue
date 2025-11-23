"""
FastAPI Backend - Standard API for Chatbot
Provides REST endpoints for all frontend interfaces
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core import ChatbotBackend

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

app = FastAPI(
    title="AI Chatbot API",
    description="Standard API for AI Chatbot with LangGraph backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot backend
chatbot_backend = ChatbotBackend()

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_id: str

class SessionRequest(BaseModel):
    session_id: Optional[str] = None
    system_prompt: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created: bool

class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

class SessionInfo(BaseModel):
    session_id: str
    exists: bool
    summary: Optional[str] = None
    messages_count: Optional[int] = None
    messages_since_last_summary: Optional[int] = None
    tools_used: Optional[List[str]] = None
    user_preferences: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a chat message",
            "POST /session/create": "Create a new session",
            "GET /session/{session_id}": "Get session info",
            "GET /history/{session_id}": "Get chat history",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "backend": "ready"}

@app.post("/chat", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message to the chatbot"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"api_{os.urandom(8).hex()}"
        
        # Send message and get response
        response = chatbot_backend.send_message(session_id, request.message)
        
        return MessageResponse(response=response, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """Create a new chat session"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"api_{os.urandom(8).hex()}"
        
        # Initialize session
        created = chatbot_backend.initialize_session(session_id, request.system_prompt)
        
        return SessionResponse(session_id=session_id, created=created)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a session"""
    try:
        info = chatbot_backend.get_session_info(session_id)
        return SessionInfo(**info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")

@app.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = chatbot_backend.get_chat_history(session_id)
        return ChatHistory(session_id=session_id, messages=messages)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session (placeholder - implement based on your needs)"""
    # This would require implementing session deletion in the backend
    return {"message": f"Session {session_id} deletion requested", "note": "Implement session deletion in backend"}

@app.get("/sessions")
async def list_sessions():
    """List all sessions (placeholder - implement based on your needs)"""
    # This would require implementing session listing in the backend
    return {"message": "Session listing requested", "note": "Implement session listing in backend"}

if __name__ == "__main__":
    # Get port from environment
    port = int(os.getenv("API_PORT", "8001"))
    
    print(f"🚀 Starting AI Chatbot API on port {port}")
    print(f"📝 API documentation available at: http://localhost:{port}/docs")
    print(f"🔍 API JSON schema available at: http://localhost:{port}/openapi.json")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["./backend", "./backend/api"]
    )
