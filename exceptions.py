"""Excepciones propias del gestor de contraseñas."""


class PasswordManagerError(Exception):
    """Base de todas las excepciones del gestor."""


class VaultExistsError(PasswordManagerError):
    """Se intenta crear una bóveda que ya existe."""


class VaultNotFoundError(PasswordManagerError):
    """No se encuentra el archivo de bóveda."""


class VaultCorruptedError(PasswordManagerError):
    """El archivo de bóveda no tiene el formato esperado."""


class AuthenticationError(PasswordManagerError):
    """Contraseña maestra incorrecta o bóveda bloqueada."""


class EntryNotFoundError(PasswordManagerError):
    """No existe la entrada solicitada."""


class DuplicateEntryError(PasswordManagerError):
    """Ya existe una entrada con el mismo servicio/usuario."""
