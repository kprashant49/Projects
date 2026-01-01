import os
from cryptography.fernet import Fernet
import json

def load_secure_config(path="config.enc"):
    key = os.getenv("CONFIG_KEY")
    if not key:
        raise RuntimeError("CONFIG_KEY environment variable not set")

    fernet = Fernet(key.encode())

    with open(path, "rb") as f:
        decrypted = fernet.decrypt(f.read())

    return decrypted.decode()

config = json.loads(load_secure_config())