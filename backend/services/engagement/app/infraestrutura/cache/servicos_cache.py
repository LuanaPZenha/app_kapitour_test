"""Serviços de engajamento com cache Redis."""

from app.dominio.casos_de_uso.servicos import ServicoAvaliacao, ServicoFavoritos
from kapitour_shared.cache.cache_service import ServicoCache


class ServicoFavoritosComCache(ServicoFavoritos):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="engagement")

    def listar_com_pontos(self, usuario_id: int) -> list[dict]:
        chave = f"favoritos:{usuario_id}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoFavoritos.listar_com_pontos(self, usuario_id),
            ttl=120,
        )


class ServicoAvaliacaoComCache(ServicoAvaliacao):
    def __init__(self, repositorio, cache: ServicoCache | None = None):
        super().__init__(repositorio)
        self._cache = cache or ServicoCache(prefixo="engagement")

    def listar(self, ponto_id: int | None = None, usuario_id: int | None = None):
        if ponto_id and not usuario_id:
            chave = f"avaliacoes:ponto:{ponto_id}"
            return self._cache.obter_ou_carregar(
                chave,
                lambda: ServicoAvaliacao.listar(self, ponto_id=ponto_id),
                ttl=300,
            )
        return ServicoAvaliacao.listar(self, ponto_id=ponto_id, usuario_id=usuario_id)

    def media_por_ponto(self, ponto_id: int) -> dict:
        chave = f"avaliacoes:media:{ponto_id}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoAvaliacao.media_por_ponto(self, ponto_id),
            ttl=300,
        )
