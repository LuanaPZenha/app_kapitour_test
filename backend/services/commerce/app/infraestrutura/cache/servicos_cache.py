"""Serviços de commerce com cache Redis."""

from app.dominio.casos_de_uso.servicos import ServicoCupom
from app.infraestrutura.persistencia.repositorios import RepositorioLoja
from kapitour_shared.cache.cache_service import ServicoCache


class ServicoCupomComCache(ServicoCupom):
    def __init__(self, *args, cache: ServicoCache | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = cache or ServicoCache(prefixo="commerce")

    def listar_disponiveis(self, parceiro_id: int | None = None) -> list[dict]:
        chave = f"cupons:disponiveis:{parceiro_id or 'all'}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoCupom.listar_disponiveis(self, parceiro_id),
            ttl=300,
        )

    def listar_resgatados(self, usuario_id: int) -> list[dict]:
        chave = f"cupons:resgatados:{usuario_id}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoCupom.listar_resgatados(self, usuario_id),
            ttl=120,
        )

    def campanhas_parceiro(self, parceiro_id: int) -> list[dict]:
        chave = f"campanhas:parceiro:{parceiro_id}"
        return self._cache.obter_ou_carregar(
            chave,
            lambda: ServicoCupom.campanhas_parceiro(self, parceiro_id),
            ttl=300,
        )


class RepositorioLojaComCache:
    """Wrapper de cache para catálogo de produtos."""

    def __init__(self, repositorio: RepositorioLoja, cache: ServicoCache | None = None):
        self._repo = repositorio
        self._cache = cache or ServicoCache(prefixo="commerce")

    def listar_produtos(self):
        return self._cache.obter_ou_carregar(
            "produtos:all", lambda: self._repo.listar_produtos(), ttl=600
        )

    def listar_tipos(self):
        return self._cache.obter_ou_carregar(
            "tipos_produto:all", lambda: self._repo.listar_tipos(), ttl=600
        )

    def listar_estoque(self):
        return self._cache.obter_ou_carregar(
            "estoque:all", lambda: self._repo.listar_estoque(), ttl=300
        )
