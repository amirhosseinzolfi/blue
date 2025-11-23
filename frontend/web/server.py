"""
Simple Web Server for Custom Web Interface
Serves static files for the chatbot web interface
"""

import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables
from dotenv import load_dotenv
load_dotenv("config/.env")

app = FastAPI(title="AI Chatbot Web Interface")

# Get the directory of this file
current_dir = Path(__file__).parent

# Mount static files
app.mount("/static", StaticFiles(directory=current_dir), name="static")

@app.get("/")
async def serve_index():
    """Serve the main index.html file"""
    return FileResponse(current_dir / "index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "interface": "web"}

if __name__ == "__main__":
    port = int(os.getenv("WEB_UI_PORT", "8002"))
    
    print(f"🚀 Starting Web Interface on port {port}")
    print(f"🌐 Access the web interface at: http://localhost:{port}")
    print(f"📱 Make sure the API is running on port {os.getenv('API_PORT', '8001')}")
    
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
