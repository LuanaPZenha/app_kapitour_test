from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Usuario:
    """Entidade de domínio — sem dependência de ORM ou HTTP."""

    id: int
    auth_id: str
    nome: str
    email: str
    tipo_usuario_id: int
    cpf: str | None = None
    sexo: str | None = None
    data_nascimento: date | None = None
    data_criacao: datetime | None = None
