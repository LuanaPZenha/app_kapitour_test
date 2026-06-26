from typing import Protocol


class ContratoGeradorToken(Protocol):
    """Porta de infraestrutura para emissão de JWT."""

    def __call__(self, auth_id: str, usuario_id: int) -> str: ...
