#!/usr/bin/env python3
"""
Quick test of the chatbot backend
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🧪 Testing Backend Import...")
    from backend.core import ChatbotBackend
    print("✅ Import successful!")
    
    print("🧪 Testing Backend Initialization...")
    backend = ChatbotBackend()
    print("✅ Backend initialized!")
    
    print("🧪 Testing Session Creation...")
    session_id = 'test_session'
    backend.initialize_session(session_id)
    print("✅ Session created!")
    
    print("🧪 Testing Message Sending...")
    response = backend.send_message(session_id, "Hello! What's 2+2?")
    print(f"✅ Response received: {response[:100]}...")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
