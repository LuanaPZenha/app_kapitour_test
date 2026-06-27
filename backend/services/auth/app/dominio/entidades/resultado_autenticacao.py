from dataclasses import dataclass

from app.dominio.entidades.usuario import Usuario


@dataclass
class ResultadoAutenticacao:
    token: str
    usuario: Usuario
    refresh_token: str | None = None
