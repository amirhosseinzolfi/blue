"""
Minimal Backend Test - No External Dependencies
"""

import os
import uuid
from typing import Annotated, Literal, List, Optional, Dict, Any
import operator
from datetime import datetime

from langchain_core.messages import (
    BaseMessage, HumanMessage, AIMessage, SystemMessage, RemoveMessage
)

# Mock LLM for testing
class MockLLM:
    def invoke(self, messages):
        # Return a simple mock response
        class MockResponse:
            def __init__(self, content):
                self.content = content
                self.id = str(uuid.uuid4())
        
        last_human_msg = None
        for msg in messages:
            if isinstance(msg, HumanMessage):
                last_human_msg = msg.content
        
        if last_human_msg:
            if "2+2" in last_human_msg or "calculate" in last_human_msg.lower():
                response_content = "The answer to 2+2 is 4."
            elif "hello" in last_human_msg.lower():
                response_content = f"Hello! I'm a test AI assistant. You said: {last_human_msg}"
            else:
                response_content = f"I received your message: {last_human_msg}. This is a test response."
        else:
            response_content = "Hello! I'm a test AI assistant."
        
        return MockResponse(response_content)

# Simple test function
def test_mock_backend():
    print("🧪 Testing Mock Backend...")
    
    # Test LLM
    llm = MockLLM()
    response = llm.invoke([HumanMessage(content="Hello! What's 2+2?")])
    print(f"✅ Mock LLM response: {response.content}")
    
    print("🎉 Mock backend test passed!")

if __name__ == "__main__":
    test_mock_backend()
