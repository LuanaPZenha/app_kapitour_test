"""Factory: monta repositórios e serviços do domínio de conteúdo turístico."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import RepositorioCategoria, RepositorioPonto, RepositorioRota
from app.servicos import ServicoCategorias, ServicoPontos, ServicoRotas
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_repositorio_categoria(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioCategoria:
    return RepositorioCategoria(sessao)


def obter_repositorio_ponto(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioPonto:
    return RepositorioPonto(sessao)


def obter_repositorio_rota(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioRota:
    return RepositorioRota(sessao)


def obter_servico_categorias(
    repositorio: RepositorioCategoria = Depends(obter_repositorio_categoria),
) -> ServicoCategorias:
    return ServicoCategorias(repositorio)


def obter_servico_pontos(
    repositorio: RepositorioPonto = Depends(obter_repositorio_ponto),
) -> ServicoPontos:
    return ServicoPontos(repositorio)


def obter_servico_rotas(
    repositorio_rota: RepositorioRota = Depends(obter_repositorio_rota),
    repositorio_ponto: RepositorioPonto = Depends(obter_repositorio_ponto),
) -> ServicoRotas:
    return ServicoRotas(repositorio_rota, repositorio_ponto)
