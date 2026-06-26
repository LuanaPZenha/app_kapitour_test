from abc import ABC, abstractmethod


class CriterioConquista(ABC):
    """OCP: critérios de desbloqueio extensíveis por código de conquista."""

    @abstractmethod
    def atende(self, estatisticas: dict) -> bool: ...


class CriterioVisitadosMinimos(CriterioConquista):
    def __init__(self, minimo: int):
        self._minimo = minimo

    def atende(self, estatisticas: dict) -> bool:
        return estatisticas["visitados"] >= self._minimo


class CriterioCarimbosMinimos(CriterioConquista):
    def __init__(self, minimo: int):
        self._minimo = minimo

    def atende(self, estatisticas: dict) -> bool:
        return estatisticas["carimbos"] >= self._minimo


REGISTRO_CRITERIOS_CONQUISTA: dict[str, CriterioConquista] = {
    "explorador_marica": CriterioVisitadosMinimos(1),
    "cacador_historias": CriterioVisitadosMinimos(3),
    "fotografo_urbano": CriterioVisitadosMinimos(5),
    "guardiao_natureza": CriterioVisitadosMinimos(8),
    "colecionador_carimbos": CriterioCarimbosMinimos(5),
}
