#!/usr/bin/env python3
"""
AI Chatbot Platform - Main Entry Point
Supports multiple frontends: Chainlit, Telegram, Custom Web UI
"""

import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    requirements = [
        "langchain",
        "langchain-openai",
        "langchain-ollama", 
        "langgraph",
        "chainlit",
        "python-telegram-bot",
        "fastapi",
        "uvicorn",
        "sqlite3",
        "python-dotenv",
        "aiofiles",
        "websockets"
    ]
    
    print("Installing dependencies...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✓ {req}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {req}: {e}")

def setup_project():
    """Setup project structure"""
    print("Setting up project structure...")
    
    # Create directories
    dirs = [
        "backend",
        "frontend/chainlit",
        "frontend/telegram", 
        "frontend/web",
        "backend/agents",
        "backend/memory",
        "backend/tools",
        "backend/api",
        "data",
        "config"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {dir_path}/")

def run_chainlit():
    """Run Chainlit interface"""
    print("🚀 Starting Chainlit interface...")
    os.chdir("frontend/chainlit")
    os.system("chainlit run app.py --port 8000")

def run_telegram():
    """Run Telegram bot"""
    print("🚀 Starting Telegram bot...")
    os.chdir("frontend/telegram")
    os.system("python bot.py")

def run_web():
    """Run custom web interface"""
    print("🚀 Starting custom web interface...")
    os.chdir("frontend/web")
    os.system("python server.py")

def run_api():
    """Run API backend"""
    print("🚀 Starting API backend...")
    os.chdir("backend/api")
    os.system("python api.py")

def run_terminal():
    """Run terminal interface"""
    print("🚀 Starting terminal interface...")
    sys.path.append("backend")
    from core import ChatbotBackend, run_terminal_chat
    backend = ChatbotBackend()
    run_terminal_chat(backend)

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            install_dependencies()
            setup_project()
            print("\n✅ Installation complete!")
            print("\nNext steps:")
            print("1. Configure your environment variables in config/.env")
            print("2. Run different interfaces:")
            print("   python main.py chainlit  # Chainlit web interface")
            print("   python main.py telegram  # Telegram bot")
            print("   python main.py web       # Custom web interface") 
            print("   python main.py api       # API backend only")
            print("   python main.py terminal  # Terminal interface")
            return
        
        elif command == "chainlit":
            run_chainlit()
            return
            
        elif command == "telegram":
            run_telegram()
            return
            
        elif command == "web":
            run_web()
            return
            
        elif command == "api":
            run_api()
            return
            
        elif command == "terminal":
            run_terminal()
            return
    
    # If no valid argument, show usage
    print("🤖 AI Chatbot Platform")
    print("="*50)
    print("Usage:")
    print("  python main.py install   # Install dependencies and setup")
    print("  python main.py chainlit  # Run Chainlit web interface")
    print("  python main.py telegram  # Run Telegram bot")
    print("  python main.py web       # Run custom web interface")
    print("  python main.py api       # Run API backend only")
    print("  python main.py terminal  # Run terminal interface")
    print("")
    print("Features:")
    print("  ✅ LangGraph-powered AI agent with tools")
    print("  ✅ Memory management & conversation summarization")
    print("  ✅ Multiple frontend options")
    print("  ✅ Standard REST API for easy integration")
    print("  ✅ Persistent chat history")
    print("  ✅ Tool calling capabilities")

if __name__ == "__main__":
    main()
