from app.validadores.contexto import ContextoResgateCupom
from app.validadores.regras import ValidadorResgateCupom


class CadeiaValidacaoResgateCupom:
    """SRP: orquestra validadores sem conhecer cada regra (OCP via composição)."""

    def __init__(self, validadores: list[ValidadorResgateCupom]):
        self._validadores = validadores

    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        for validador in self._validadores:
            erro = validador.validar(contexto)
            if erro:
                return erro
        return None
