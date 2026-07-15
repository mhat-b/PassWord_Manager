"""Lógica de negocio de alto nivel: generación y evaluación de contraseñas."""

import random
import string

from vault import PasswordVault

SYMBOLS = "!@#$%^&*()-_=+[]{}"


class PasswordManager:
    """Envuelve la bóveda y ofrece utilidades adicionales (generador, fuerza)."""

    def __init__(self, vault: PasswordVault):
        self.vault = vault

    @staticmethod
    def generate_password(
        length: int = 16,
        use_upper: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
    ) -> str:
        if length < 4:
            raise ValueError("La longitud mínima de una contraseña generada es 4.")

        pool = list(string.ascii_lowercase)
        required = [random.choice(string.ascii_lowercase)]

        if use_upper:
            pool += list(string.ascii_uppercase)
            required.append(random.choice(string.ascii_uppercase))
        if use_digits:
            pool += list(string.digits)
            required.append(random.choice(string.digits))
        if use_symbols:
            pool += list(SYMBOLS)
            required.append(random.choice(SYMBOLS))

        remaining_count = max(length - len(required), 0)
        remaining = [random.choice(pool) for _ in range(remaining_count)]

        chars = (required + remaining)[:length]
        random.shuffle(chars)
        return "".join(chars)

    @staticmethod
    def evaluate_strength(password: str) -> str:
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in SYMBOLS for c in password):
            score += 1

        levels = ["Muy débil", "Débil", "Aceptable", "Buena", "Fuerte", "Muy fuerte", "Excelente"]
        return levels[min(score, len(levels) - 1)]
