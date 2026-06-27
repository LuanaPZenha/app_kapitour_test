import re
from uuid import uuid4

import bleach


def sanitizar_texto(valor: str, max_length: int = 1000) -> str:
    """Remove tags HTML e limita tamanho."""
    if not valor:
        return valor
    sem_blocos_perigosos = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        "",
        valor,
        flags=re.IGNORECASE | re.DOTALL,
    )
    limpo = bleach.clean(sem_blocos_perigosos, tags=[], attributes={}, strip=True)
    return limpo[:max_length]


def sanitizar_email(email: str) -> str:
    return email.strip().lower()


def validar_senha_forte(senha: str) -> list[str]:
    """Retorna lista de erros de validação (vazia = OK)."""
    erros = []
    if len(senha) < 8:
        erros.append("Senha deve ter no mínimo 8 caracteres.")
    if not re.search(r"[A-Z]", senha):
        erros.append("Senha deve conter ao menos uma letra maiúscula.")
    if not re.search(r"[a-z]", senha):
        erros.append("Senha deve conter ao menos uma letra minúscula.")
    if not re.search(r"\d", senha):
        erros.append("Senha deve conter ao menos um número.")
    return erros


def gerar_token_aleatorio() -> str:
    return str(uuid4())
