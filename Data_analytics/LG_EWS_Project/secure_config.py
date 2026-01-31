import json
import os
from cryptography.fernet import Fernet


def load_secure_config():
    # Load non-secret config
    with open("config.json") as f:
        config = json.load(f)

    # Load encryption key
    key = os.getenv("SECRETS_KEY")
    if not key:
        raise RuntimeError("SECRETS_KEY env variable not set")

    fernet = Fernet(key.encode())

    # Decrypt secrets
    with open("secrets.enc", "rb") as f:
        secrets = json.loads(fernet.decrypt(f.read()).decode())

    # Merge secrets into config
    _deep_merge(config, secrets)

    return config


def _deep_merge(target, source):
    """
    Recursively merge source into target
    """
    for key, value in source.items():
        if isinstance(value, dict) and key in target:
            _deep_merge(target[key], value)
        else:
            target[key] = value
