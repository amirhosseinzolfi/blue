#!/usr/bin/env python3
"""
Quick test script for the chatbot backend
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '/root/blue/chat')

try:
    from backend.core import ChatbotBackend
    
    print("🧪 Testing AI Chatbot Backend...")
    print("=" * 40)
    
    # Initialize backend
    backend = ChatbotBackend()
    print("✅ Backend initialized successfully!")
    
    # Create test session
    session_id = 'test_session_123'
    backend.initialize_session(session_id)
    print(f"✅ Session created: {session_id}")
    
    # Test basic message
    response1 = backend.send_message(session_id, 'Hello! How are you?')
    print(f"📤 User: Hello! How are you?")
    print(f"📥 Bot: {response1}")
    print()
    
    # Test calculation tool
    response2 = backend.send_message(session_id, 'Can you calculate 15 * 23 for me?')
    print(f"📤 User: Can you calculate 15 * 23 for me?")
    print(f"📥 Bot: {response2}")
    print()
    
    # Test time tool
    response3 = backend.send_message(session_id, 'What time is it?')
    print(f"📤 User: What time is it?")
    print(f"📥 Bot: {response3}")
    print()
    
    # Get session info
    info = backend.get_session_info(session_id)
    print("📊 Session Info:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
