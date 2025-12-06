#!/usr/bin/env python3
"""
Generate bcrypt hash of the PLAIN_PASSWORD env var and print to stdout
"""
import os
from passlib.context import CryptContext

pwd = os.environ.get('PLAIN_PASSWORD')
if not pwd:
    print('PLAIN_PASSWORD is required')
    raise SystemExit(1)
ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(ctx.hash(pwd))
