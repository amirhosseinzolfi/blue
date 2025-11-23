#!/usr/bin/env python3
"""
Simple launcher to test and run the chatbot
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_backend():
    """Test the backend functionality"""
    try:
        print("🧪 Testing AI Chatbot Backend...")
        
        from backend.core import ChatbotBackend
        print("✅ Backend imported successfully!")
        
        # Test initialization
        backend = ChatbotBackend()
        print("✅ Backend initialized!")
        
        # Test session creation
        session_id = 'test_session'
        backend.initialize_session(session_id)
        print(f"✅ Session created: {session_id}")
        
        print("🎉 Backend test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_api():
    """Run the API server"""
    try:
        from backend.api.api import app
        import uvicorn
        print("🚀 Starting API server...")
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"❌ Failed to start API: {e}")

def run_terminal():
    """Run terminal interface"""
    try:
        from backend.core import ChatbotBackend, run_terminal_chat
        backend = ChatbotBackend()
        run_terminal_chat(backend)
    except Exception as e:
        print(f"❌ Failed to start terminal interface: {e}")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_backend()
        elif command == "api":
            run_api()
        elif command == "terminal":
            run_terminal()
        else:
            print("Unknown command. Use: test, api, or terminal")
    else:
        print("🤖 AI Chatbot Launcher")
        print("Usage:")
        print("  python launcher.py test     # Test backend")
        print("  python launcher.py api      # Run API server")
        print("  python launcher.py terminal # Run terminal interface")

if __name__ == "__main__":
    main()
