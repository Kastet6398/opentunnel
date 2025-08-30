#!/usr/bin/env python3
"""Generate a secure secret key for JWT authentication."""

import secrets
import string


def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(f"Generated secret key: {secret_key}")
    print("\nAdd this to your .env file:")
    print(f"SECRET_KEY={secret_key}")