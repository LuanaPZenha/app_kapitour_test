"""Serviços de domínio com cache Redis (cache-aside)."""

from app.apresentacao.mapeadores import mapear_categorias, mapear_pontos, mapear_rotas
from app.dominio.casos_de_uso.servicos import CasoListarCategorias, CasoListarPontos, CasoListarRotas
from kapitour_shared.cache.cache_service import ServicoCache


def _para_cache(respostas):
    return [item.model_dump(mode="json") for item in respostas]


class ServicoCategoriasComCache(CasoListarCategorias):
    def __init__(self, repositorio, cache: ServicoCache | None = None):
        super().__init__(repositorio)
        self._cache = cache or ServicoCache(prefixo="content")

    def listar(self):
        def carregar():
            return _para_cache(mapear_categorias(CasoListarCategorias.listar(self)))

        dados = self._cache.obter_ou_carregar("categorias:all", carregar, ttl=600)
        return mapear_categorias(dados or [])


class ServicoPontosComCache(CasoListarPontos):
    def __init__(self, repositorio, cache: ServicoCache | None = None):
        super().__init__(repositorio)
        self._cache = cache or ServicoCache(prefixo="content")

    def listar(self, categoria_id: int | None = None):
        chave = f"pontos:list:{categoria_id or 'all'}"

        def carregar():
            return _para_cache(mapear_pontos(CasoListarPontos.listar(self, categoria_id)))

        dados = self._cache.obter_ou_carregar(chave, carregar, ttl=300)
        return mapear_pontos(dados or [])

    def buscar_por_id(self, ponto_id: int):
        chave = f"pontos:id:{ponto_id}"

        def carregar():
            ponto = CasoListarPontos.buscar_por_id(self, ponto_id)
            return mapear_pontos([ponto])[0].model_dump(mode="json") if ponto else None

        dados = self._cache.obter_ou_carregar(chave, carregar, ttl=300)
        if not dados:
            return None
        return mapear_pontos([dados])[0]

    def buscar_por_ids(self, ids: list[int]):
        if not ids:
            return []
        chave = f"pontos:batch:{','.join(map(str, sorted(ids)))}"

        def carregar():
            return _para_cache(mapear_pontos(CasoListarPontos.buscar_por_ids(self, ids)))

        dados = self._cache.obter_ou_carregar(chave, carregar, ttl=300)
        return mapear_pontos(dados or [])


class ServicoRotasComCache(CasoListarRotas):
    def __init__(self, repositorio_rota, repositorio_ponto, cache: ServicoCache | None = None):
        super().__init__(repositorio_rota, repositorio_ponto)
        self._cache = cache or ServicoCache(prefixo="content")

    def listar(self):
        def carregar():
            return _para_cache(mapear_rotas(CasoListarRotas.listar(self)))

        dados = self._cache.obter_ou_carregar("rotas:all", carregar, ttl=600)
        return mapear_rotas(dados or [])

    def pontos_da_rota(self, rota_id: int):
        chave = f"rotas:pontos:{rota_id}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: CasoListarRotas.pontos_da_rota(self, rota_id),
            ttl=300,
        )
