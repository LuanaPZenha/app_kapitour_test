from abc import ABC, abstractmethod

from app.repositorios import RepositorioRanking


class EstrategiaRanking(ABC):
    """OCP: novas categorias de ranking estendem sem alterar ServicoRanking."""

    @property
    @abstractmethod
    def unidade(self) -> str: ...

    @abstractmethod
    def buscar_linhas(
        self, repositorio: RepositorioRanking, pagina: int, tamanho: int
    ) -> list: ...


class EstrategiaRankingCheckins(EstrategiaRanking):
    @property
    def unidade(self) -> str:
        return "locais"

    def buscar_linhas(self, repositorio: RepositorioRanking, pagina: int, tamanho: int) -> list:
        return repositorio.ranking_checkins(pagina, tamanho)


class EstrategiaRankingCarimbos(EstrategiaRanking):
    @property
    def unidade(self) -> str:
        return "carimbos"

    def buscar_linhas(self, repositorio: RepositorioRanking, pagina: int, tamanho: int) -> list:
        return repositorio.ranking_carimbos(pagina, tamanho)


class EstrategiaRankingEco(EstrategiaRanking):
    @property
    def unidade(self) -> str:
        return "ecopontos"

    def buscar_linhas(self, repositorio: RepositorioRanking, pagina: int, tamanho: int) -> list:
        return repositorio.ranking_eco(pagina, tamanho)


class EstrategiaRankingXp(EstrategiaRanking):
    @property
    def unidade(self) -> str:
        return "xp"

    def buscar_linhas(self, repositorio: RepositorioRanking, pagina: int, tamanho: int) -> list:
        return repositorio.ranking_xp(pagina, tamanho)


REGISTRO_ESTRATEGIAS_RANKING: dict[str, EstrategiaRanking] = {
    "exploradores": EstrategiaRankingCheckins(),
    "trilheiros": EstrategiaRankingCheckins(),
    "colecionadores": EstrategiaRankingCarimbos(),
    "ecopass": EstrategiaRankingEco(),
    "xp": EstrategiaRankingXp(),
}
