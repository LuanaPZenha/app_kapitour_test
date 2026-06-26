from abc import ABC, abstractmethod

from app.dominio.eventos.modelo import ContextoCheckin


class ObservadorCheckin(ABC):
    """Observer: reage a um check-in sem acoplar o fluxo principal."""

    @property
    @abstractmethod
    def chave_resultado(self) -> str | None:
        """Chave para agregar no retorno do publicador, ou None se sem retorno."""

    @abstractmethod
    def notificar(self, contexto: ContextoCheckin): ...


class ObservadorConquistas(ObservadorCheckin):
    @property
    def chave_resultado(self) -> str:
        return "novas_conquistas"

    def notificar(self, contexto: ContextoCheckin):
        return contexto.gamificacao.avaliar_conquistas(contexto.usuario_id)


class ObservadorMissoes(ObservadorCheckin):
    @property
    def chave_resultado(self) -> str | None:
        return None

    def notificar(self, contexto: ContextoCheckin):
        contexto.gamificacao.avaliar_missoes(contexto.usuario_id)


class ObservadorDiario(ObservadorCheckin):
    @property
    def chave_resultado(self) -> str | None:
        return None

    def notificar(self, contexto: ContextoCheckin):
        contexto.gamificacao.registrar_diario_primeira_visita(
            contexto.usuario_id,
            contexto.ponto_id,
            contexto.ponto,
            contexto.checkin,
            contexto.primeira_visita,
        )
