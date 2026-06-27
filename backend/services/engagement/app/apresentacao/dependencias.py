from fastapi import Depends
from sqlalchemy.orm import Session

from app.infraestrutura.cache.servicos_cache import ServicoAvaliacaoComCache, ServicoFavoritosComCache
from app.infraestrutura.persistencia.repositorios import RepositorioAvaliacao, RepositorioFavorito
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.cache.cache_service import ServicoCache
from kapitour_shared.contratos.clientes_http import ContratoClienteConteudo
from kapitour_shared.fabricas import obter_cliente_conteudo


def obter_cache_engagement() -> ServicoCache:
    return ServicoCache(prefixo="engagement")


def obter_repositorio_favorito(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioFavorito:
    return RepositorioFavorito(sessao)


def obter_repositorio_avaliacao(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioAvaliacao:
    return RepositorioAvaliacao(sessao)


def obter_servico_favoritos(
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
    cache: ServicoCache = Depends(obter_cache_engagement),
) -> ServicoFavoritosComCache:
    return ServicoFavoritosComCache(favoritos=repositorio, conteudo=conteudo, cache=cache)


def obter_servico_avaliacao(
    repositorio: RepositorioAvaliacao = Depends(obter_repositorio_avaliacao),
    cache: ServicoCache = Depends(obter_cache_engagement),
) -> ServicoAvaliacaoComCache:
    return ServicoAvaliacaoComCache(repositorio, cache=cache)
