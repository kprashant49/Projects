from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
print("SAVE THIS KEY SECURELY:", key.decode())

fernet = Fernet(key)

with open("secrets.json", "rb") as f:
    encrypted = fernet.encrypt(f.read())

with open("secrets.enc", "wb") as f:
    f.write(encrypted)

print("secrets.json encrypted to secrets.enc")
