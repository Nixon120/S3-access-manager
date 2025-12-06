#!/usr/bin/env python3
import os
import bcrypt
pw = os.environ.get('PLAIN_PASSWORD')
if not pw:
    print('PLAIN_PASSWORD env var required')
    raise SystemExit(1)
print(bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode())
