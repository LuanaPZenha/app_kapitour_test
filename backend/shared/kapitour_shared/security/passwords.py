import re

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    """Gera hash Argon2 para novas senhas."""
    return _ph.hash(senha)


def _eh_hash_bcrypt(senha_hash: str) -> bool:
    return senha_hash.startswith("$2")


def senha_confere(senha_informada: str, senha_hash: str) -> bool:
    """Verifica senha — suporta Argon2 (novo) e bcrypt (legado)."""
    if _eh_hash_bcrypt(senha_hash):
        return bcrypt.checkpw(
            senha_informada.encode("utf-8"),
            senha_hash.encode("utf-8"),
        )
    try:
        _ph.verify(senha_hash, senha_informada)
        return True
    except VerifyMismatchError:
        return False


def precisa_rehash(senha_hash: str) -> bool:
    """Indica se hash legado bcrypt deve ser migrado para Argon2."""
    return _eh_hash_bcrypt(senha_hash)
