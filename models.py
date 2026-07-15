"""Modelo de datos: una entrada de contraseña."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


@dataclass
class PasswordEntry:
    service: str
    username: str
    password: str
    url: str = ""
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PasswordEntry":
        return cls(**data)

    def touch(self) -> None:
        self.updated_at = datetime.now().isoformat(timespec="seconds")
