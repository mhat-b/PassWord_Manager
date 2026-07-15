"""Tests de PasswordManager (generador y evaluador de fuerza)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import PasswordManager


class TestPasswordGenerator(unittest.TestCase):
    def test_default_length(self):
        pwd = PasswordManager.generate_password()
        self.assertEqual(len(pwd), 16)

    def test_custom_length(self):
        pwd = PasswordManager.generate_password(length=24)
        self.assertEqual(len(pwd), 24)

    def test_too_short_raises(self):
        with self.assertRaises(ValueError):
            PasswordManager.generate_password(length=2)

    def test_only_lowercase_when_disabled(self):
        pwd = PasswordManager.generate_password(
            length=20, use_upper=False, use_digits=False, use_symbols=False
        )
        self.assertTrue(all(c.islower() for c in pwd))

    def test_contains_required_categories(self):
        pwd = PasswordManager.generate_password(length=20)
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))


class TestStrengthEvaluator(unittest.TestCase):
    def test_weak_password(self):
        self.assertEqual(PasswordManager.evaluate_strength("abc"), "Débil")

    def test_empty_password_is_muy_debil(self):
        self.assertEqual(PasswordManager.evaluate_strength(""), "Muy débil")

    def test_strong_password(self):
        result = PasswordManager.evaluate_strength("Abc123!@#xyzLMN")
        self.assertIn(result, ["Fuerte", "Muy fuerte", "Excelente"])


if __name__ == "__main__":
    unittest.main()
