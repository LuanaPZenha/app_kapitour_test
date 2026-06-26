from abc import ABC, abstractmethod


class EstrategiaProgressoMissao(ABC):
    """Strategy: calcula progresso conforme o tipo da missão (OCP)."""

    @abstractmethod
    def calcular_progresso(self, estatisticas: dict) -> int: ...


class EstrategiaMissaoVisitados(EstrategiaProgressoMissao):
    def calcular_progresso(self, estatisticas: dict) -> int:
        return estatisticas["visitados"]


class EstrategiaMissaoCarimbos(EstrategiaProgressoMissao):
    def calcular_progresso(self, estatisticas: dict) -> int:
        return estatisticas["carimbos"]


REGISTRO_ESTRATEGIAS_MISSAO: dict[str, EstrategiaProgressoMissao] = {
    "carimbos": EstrategiaMissaoCarimbos(),
    "visitados": EstrategiaMissaoVisitados(),
}

ESTRATEGIA_MISSAO_PADRAO = EstrategiaMissaoVisitados()
