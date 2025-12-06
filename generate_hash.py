import bcrypt

# Password to hash
password = "Maya100$"

# Generate salt and hash
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print(f"Password hash for 'Maya100$':")
print(hashed.decode('utf-8'))
