#!/usr/bin/env python3
"""
Test password verification
"""
import bcrypt

# The hash we stored in database
stored_hash = "$2b$12$HiBZMiL16XB1CqMi6seFkO2KU.8u0khK0MUJRGNimSNbrJzr0yhe."
password = "Maya100$"

# Test verification
result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
print(f"Password: {password}")
print(f"Hash: {stored_hash}")
print(f"Verification result: {result}")

# Also test with passlib
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    result2 = pwd_context.verify(password, stored_hash)
    print(f"Passlib verification result: {result2}")
except Exception as e:
    print(f"Passlib error: {e}")
