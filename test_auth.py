#!/usr/bin/env python3
import sys
sys.path.append('/root/blue')

from auth import auth_callback

# Test the auth function
print("Testing auth callback...")

# Test new user signup
result1 = auth_callback("+1234567890", "password123")
print(f"New user test: {result1}")

# Test existing user login
result2 = auth_callback("+1234567890", "password123")
print(f"Existing user test: {result2}")

# Test wrong password
result3 = auth_callback("+1234567890", "wrongpass")
print(f"Wrong password test: {result3}")

# Test invalid phone
result4 = auth_callback("invalid", "password123")
print(f"Invalid phone test: {result4}")