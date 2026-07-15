"""Bóveda de contraseñas: persistencia cifrada en disco (JSON + Fernet)."""

import base64
import json
from pathlib import Path
from typing import Dict, List

from cryptography.fernet import Fernet, InvalidToken

from crypto_utils import derive_key, generate_salt
from exceptions import (
    AuthenticationError,
    DuplicateEntryError,
    EntryNotFoundError,
    VaultCorruptedError,
    VaultExistsError,
    VaultNotFoundError,
)
from models import PasswordEntry

VERIFIER_TOKEN = b"VAULT_OK"


class PasswordVault:
    """Representa un archivo de bóveda cifrado en disco."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._key: bytes | None = None
        self._salt: bytes | None = None
        self._entries: Dict[str, PasswordEntry] = {}

    # ---------- estado ----------

    @property
    def is_unlocked(self) -> bool:
        return self._key is not None

    def exists(self) -> bool:
        return self.path.exists()

    def _ensure_unlocked(self) -> None:
        if not self.is_unlocked:
            raise AuthenticationError("La bóveda está bloqueada.")

    # ---------- ciclo de vida ----------

    def create(self, master_password: str) -> None:
        if self.exists():
            raise VaultExistsError(f"Ya existe una bóveda en '{self.path}'.")
        if not master_password:
            raise ValueError("La contraseña maestra no puede estar vacía.")
        self._salt = generate_salt()
        self._key = derive_key(master_password, self._salt)
        self._entries = {}
        self._save()

    def unlock(self, master_password: str) -> None:
        if not self.exists():
            raise VaultNotFoundError(f"No existe bóveda en '{self.path}'.")
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            salt = base64.b64decode(raw["salt"])
            key = derive_key(master_password, salt)
            fernet = Fernet(key)
            verifier = fernet.decrypt(base64.b64decode(raw["verifier"]))
            if verifier != VERIFIER_TOKEN:
                raise AuthenticationError("Contraseña maestra incorrecta.")
            data_blob = fernet.decrypt(base64.b64decode(raw["data"]))
            entries_raw = json.loads(data_blob.decode("utf-8"))
        except InvalidToken:
            raise AuthenticationError("Contraseña maestra incorrecta.")
        except (KeyError, json.JSONDecodeError, ValueError) as exc:
            raise VaultCorruptedError(f"Bóveda corrupta o ilegible: {exc}") from exc

        self._salt = salt
        self._key = key
        self._entries = {e["id"]: PasswordEntry.from_dict(e) for e in entries_raw}

    def lock(self) -> None:
        self._key = None
        self._salt = None
        self._entries = {}

    def _save(self) -> None:
        self._ensure_unlocked()
        fernet = Fernet(self._key)
        entries_raw = [e.to_dict() for e in self._entries.values()]
        data_blob = fernet.encrypt(json.dumps(entries_raw).encode("utf-8"))
        verifier = fernet.encrypt(VERIFIER_TOKEN)
        payload = {
            "salt": base64.b64encode(self._salt).decode("ascii"),
            "verifier": base64.b64encode(verifier).decode("ascii"),
            "data": base64.b64encode(data_blob).decode("ascii"),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ---------- CRUD ----------

    def add_entry(self, entry: PasswordEntry) -> PasswordEntry:
        self._ensure_unlocked()
        for existing in self._entries.values():
            if (
                existing.service.lower() == entry.service.lower()
                and existing.username.lower() == entry.username.lower()
            ):
                raise DuplicateEntryError(
                    f"Ya existe una entrada para '{entry.service}' / '{entry.username}'."
                )
        self._entries[entry.id] = entry
        self._save()
        return entry

    def update_entry(self, entry_id: str, **changes) -> PasswordEntry:
        self._ensure_unlocked()
        entry = self._entries.get(entry_id)
        if entry is None:
            raise EntryNotFoundError(f"No se encontró la entrada '{entry_id}'.")
        for field_name, value in changes.items():
            if hasattr(entry, field_name):
                setattr(entry, field_name, value)
        entry.touch()
        self._save()
        return entry

    def delete_entry(self, entry_id: str) -> None:
        self._ensure_unlocked()
        if entry_id not in self._entries:
            raise EntryNotFoundError(f"No se encontró la entrada '{entry_id}'.")
        del self._entries[entry_id]
        self._save()

    def get_entry(self, entry_id: str) -> PasswordEntry:
        self._ensure_unlocked()
        entry = self._entries.get(entry_id)
        if entry is None:
            raise EntryNotFoundError(f"No se encontró la entrada '{entry_id}'.")
        return entry

    def list_entries(self) -> List[PasswordEntry]:
        self._ensure_unlocked()
        return sorted(self._entries.values(), key=lambda e: e.service.lower())

    def search(self, query: str) -> List[PasswordEntry]:
        self._ensure_unlocked()
        q = query.lower().strip()
        if not q:
            return self.list_entries()
        return [
            e
            for e in self.list_entries()
            if q in e.service.lower() or q in e.username.lower() or q in e.url.lower()
        ]

    def change_master_password(self, old_password: str, new_password: str) -> None:
        self.unlock(old_password)
        if not new_password:
            raise ValueError("La nueva contraseña maestra no puede estar vacía.")
        entries = dict(self._entries)
        self._salt = generate_salt()
        self._key = derive_key(new_password, self._salt)
        self._entries = entries
        self._save()
