"""Factory: monta repositórios e serviços do domínio de conteúdo turístico."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infraestrutura.cache.servicos_cache import (
    ServicoCategoriasComCache,
    ServicoPontosComCache,
    ServicoRotasComCache,
)
from app.infraestrutura.persistencia.repositorios import RepositorioCategoria, RepositorioPonto, RepositorioRota
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_repositorio_categoria(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioCategoria:
    return RepositorioCategoria(sessao)


def obter_repositorio_ponto(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioPonto:
    return RepositorioPonto(sessao)


def obter_repositorio_rota(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioRota:
    return RepositorioRota(sessao)


def obter_servico_categorias(
    repositorio: RepositorioCategoria = Depends(obter_repositorio_categoria),
) -> ServicoCategoriasComCache:
    return ServicoCategoriasComCache(repositorio)


def obter_servico_pontos(
    repositorio: RepositorioPonto = Depends(obter_repositorio_ponto),
) -> ServicoPontosComCache:
    return ServicoPontosComCache(repositorio)


def obter_servico_rotas(
    repositorio_rota: RepositorioRota = Depends(obter_repositorio_rota),
    repositorio_ponto: RepositorioPonto = Depends(obter_repositorio_ponto),
) -> ServicoRotasComCache:
    return ServicoRotasComCache(repositorio_rota, repositorio_ponto)
