"""Factory centralizada para clientes HTTP entre microserviços (Singleton por processo)."""

from functools import lru_cache

from kapitour_shared.clientes_http import ClienteAutenticacao, ClienteConteudo
from kapitour_shared.contratos.clientes_http import (
    ContratoClienteAutenticacao,
    ContratoClienteConteudo,
)


@lru_cache(maxsize=1)
def obter_cliente_autenticacao() -> ContratoClienteAutenticacao:
    """Factory + Singleton: uma instância reutilizada por worker (config imutável)."""
    return ClienteAutenticacao()


@lru_cache(maxsize=1)
def obter_cliente_conteudo() -> ContratoClienteConteudo:
    """Factory + Singleton: evita recriar cliente HTTP a cada request."""
    return ClienteConteudo()
