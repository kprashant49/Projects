from cryptography.fernet import Fernet

# Generate key (DO THIS ONCE)
key = Fernet.generate_key()
print("SAVE THIS KEY SECURELY:", key.decode())

fernet = Fernet(key)

with open("config.json", "rb") as f:
    encrypted = fernet.encrypt(f.read())

with open("config.enc", "wb") as f:
    f.write(encrypted)

print("config.json encrypted to config.enc")