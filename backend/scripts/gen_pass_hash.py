#!/usr/bin/env python3
"""
Generate password hash using passlib's bcrypt without initializing the full context
"""
import bcrypt

# Direct bcrypt usage - no passlib
password = "Maya100$"
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print(f"Password: {password}")
print(f"Hash: {hashed.decode('utf-8')}")
