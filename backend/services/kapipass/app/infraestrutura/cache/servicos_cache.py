"""Serviços KapiPass com cache Redis."""

from app.aplicacao.servicos import (
    ServicoColecao,
    ServicoDiario,
    ServicoEco,
    ServicoGamificacao,
    ServicoMissao,
    ServicoRanking,
    ServicoTesouro,
)
from kapitour_shared.cache.cache_service import ServicoCache


def invalidar_cache_usuario(cache: ServicoCache, usuario_id: int) -> None:
    for recurso in (
        "checkins", "carimbos", "conquistas", "colecoes",
        "missoes", "eco", "diario", "tesouros", "passaporte",
    ):
        cache.invalidar(f"kapipass:{recurso}:{usuario_id}")


class ServicoGamificacaoComCache(ServicoGamificacao):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_niveis(self) -> list[dict]:
        return self._cache.obter_ou_carregar(
            "kapipass:niveis:all",
            lambda: ServicoGamificacao.listar_niveis(self),
            ttl=3600,
        )

    def listar_checkins(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:checkins:{usuario_id}",
            lambda: ServicoGamificacao.listar_checkins(self, usuario_id),
            ttl=120,
        )

    def listar_carimbos(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:carimbos:{usuario_id}",
            lambda: ServicoGamificacao.listar_carimbos(self, usuario_id),
            ttl=120,
        )

    def listar_conquistas(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:conquistas:{usuario_id}",
            lambda: ServicoGamificacao.listar_conquistas(self, usuario_id),
            ttl=120,
        )


class ServicoColecaoComCache(ServicoColecao):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_colecoes(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:colecoes:{usuario_id}",
            lambda: ServicoColecao.listar_colecoes(self, usuario_id),
            ttl=120,
        )


class ServicoMissaoComCache(ServicoMissao):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_missoes(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:missoes:{usuario_id}",
            lambda: ServicoMissao.listar_missoes(self, usuario_id),
            ttl=120,
        )


class ServicoEcoComCache(ServicoEco):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_atividades(self, usuario_id: int) -> dict:
        return self._cache.obter_ou_carregar(
            f"kapipass:eco:{usuario_id}",
            lambda: ServicoEco.listar_atividades(self, usuario_id),
            ttl=120,
        )


class ServicoDiarioComCache(ServicoDiario):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_entradas(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:diario:{usuario_id}",
            lambda: ServicoDiario.listar_entradas(self, usuario_id),
            ttl=120,
        )


class ServicoTesouroComCache(ServicoTesouro):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def listar_tesouros(self, usuario_id: int) -> list[dict]:
        return self._cache.obter_ou_carregar(
            f"kapipass:tesouros:{usuario_id}",
            lambda: ServicoTesouro.listar_tesouros(self, usuario_id),
            ttl=120,
        )


class ServicoRankingComCache(ServicoRanking):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="kapipass")

    def obter_ranking(self, categoria: str, page: int, size: int) -> dict:
        chave = f"kapipass:rankings:{categoria}:{page}:{size}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoRanking.obter_ranking(self, categoria, page, size),
            ttl=60,
        )
