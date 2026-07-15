"""Tests básicos de PasswordVault."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from exceptions import (
    AuthenticationError,
    DuplicateEntryError,
    EntryNotFoundError,
    VaultExistsError,
    VaultNotFoundError,
)
from models import PasswordEntry
from vault import PasswordVault


class TestPasswordVault(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(__file__).resolve().parent / "_tmp"
        self.tmp_dir.mkdir(exist_ok=True)
        self.vault_path = self.tmp_dir / "test_vault.dat"
        if self.vault_path.exists():
            self.vault_path.unlink()

    def tearDown(self):
        if self.vault_path.exists():
            self.vault_path.unlink()
        if self.tmp_dir.exists():
            self.tmp_dir.rmdir()

    def test_create_and_unlock(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        self.assertTrue(vault.exists())

        vault2 = PasswordVault(self.vault_path)
        vault2.unlock("master123")
        self.assertEqual(vault2.list_entries(), [])

    def test_create_twice_raises(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        with self.assertRaises(VaultExistsError):
            vault.create("master123")

    def test_unlock_missing_file_raises(self):
        vault = PasswordVault(self.vault_path)
        with self.assertRaises(VaultNotFoundError):
            vault.unlock("whatever")

    def test_wrong_password_raises(self):
        vault = PasswordVault(self.vault_path)
        vault.create("correct-password")

        vault2 = PasswordVault(self.vault_path)
        with self.assertRaises(AuthenticationError):
            vault2.unlock("wrong-password")

    def test_add_and_get_entry(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        entry = PasswordEntry(service="GitHub", username="dev", password="hunter2")
        vault.add_entry(entry)

        fetched = vault.get_entry(entry.id)
        self.assertEqual(fetched.service, "GitHub")
        self.assertEqual(fetched.password, "hunter2")

    def test_duplicate_entry_raises(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="a"))
        with self.assertRaises(DuplicateEntryError):
            vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="b"))

    def test_update_entry(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        entry = vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="a"))
        vault.update_entry(entry.id, password="nueva123")
        self.assertEqual(vault.get_entry(entry.id).password, "nueva123")

    def test_delete_entry(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        entry = vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="a"))
        vault.delete_entry(entry.id)
        with self.assertRaises(EntryNotFoundError):
            vault.get_entry(entry.id)

    def test_persistence_across_instances(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="a"))

        reopened = PasswordVault(self.vault_path)
        reopened.unlock("master123")
        self.assertEqual(len(reopened.list_entries()), 1)
        self.assertEqual(reopened.list_entries()[0].service, "GitHub")

    def test_locked_vault_raises_on_operations(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        vault.lock()
        with self.assertRaises(AuthenticationError):
            vault.list_entries()

    def test_search(self):
        vault = PasswordVault(self.vault_path)
        vault.create("master123")
        vault.add_entry(PasswordEntry(service="GitHub", username="dev", password="a"))
        vault.add_entry(PasswordEntry(service="Gmail", username="dev", password="b"))
        results = vault.search("git")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].service, "GitHub")


if __name__ == "__main__":
    unittest.main()
