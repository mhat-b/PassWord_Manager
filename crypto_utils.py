"""Derivación de clave a partir de la contraseña maestra."""

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 390_000


def generate_salt(size: int = 16) -> bytes:
    return os.urandom(size)


def derive_key(master_password: str, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    """Deriva una clave Fernet (32 bytes url-safe base64) desde la contraseña maestra."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)
