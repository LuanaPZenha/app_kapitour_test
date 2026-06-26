from dataclasses import dataclass

from app.modelos import Cupom
from app.repositorios import RepositorioCupom


@dataclass
class ContextoResgateCupom:
    """Dados compartilhados entre validadores da cadeia (SRP por regra)."""

    cupom_id: int
    usuario_id: int
    parceiro_id: int | None
    repositorio: RepositorioCupom
    cupom: Cupom | None = None
