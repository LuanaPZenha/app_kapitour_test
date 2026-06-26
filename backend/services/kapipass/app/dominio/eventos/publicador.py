from app.dominio.eventos.modelo import ContextoCheckin
from app.dominio.eventos.observadores import (
    ObservadorCheckin,
    ObservadorConquistas,
    ObservadorDiario,
    ObservadorMissoes,
)


class PublicadorEventosCheckin:
    """Observer: notifica assinantes após o check-in principal."""

    def __init__(self, observadores: list[ObservadorCheckin]):
        self._observadores = observadores

    def publicar(self, contexto: ContextoCheckin) -> dict:
        resultados: dict = {}
        for observador in self._observadores:
            valor = observador.notificar(contexto)
            if observador.chave_resultado:
                resultados[observador.chave_resultado] = valor
        return resultados


def criar_publicador_checkin_padrao() -> PublicadorEventosCheckin:
    return PublicadorEventosCheckin(
        [
            ObservadorConquistas(),
            ObservadorMissoes(),
            ObservadorDiario(),
        ]
    )
