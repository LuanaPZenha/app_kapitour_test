"""Injeção de dependências (DIP) — camada HTTP não instancia repositórios diretamente."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import RepositorioUsuario
from app.servicos import ServicoAutenticacao, ServicoUsuario
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_repositorio_usuario(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioUsuario:
    return RepositorioUsuario(sessao)


def obter_servico_autenticacao(
    repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario),
) -> ServicoAutenticacao:
    return ServicoAutenticacao(repositorio=repositorio)


def obter_servico_usuario(
    repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario),
) -> ServicoUsuario:
    return ServicoUsuario(repositorio=repositorio)
