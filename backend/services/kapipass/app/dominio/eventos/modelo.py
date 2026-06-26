from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.aplicacao.servicos import ServicoGamificacao


@dataclass
class ContextoCheckin:
    """Dados do evento de check-in para os observadores."""

    usuario_id: int
    ponto_id: int
    ponto: dict
    checkin: object
    primeira_visita: bool
    gamificacao: "ServicoGamificacao"
