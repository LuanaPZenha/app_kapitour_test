"""Composição de dependências — liga casos de uso à infraestrutura."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.dominio.casos_de_uso.autenticacao import CasoEntrarUsuario, CasoRegistrarUsuario
from app.dominio.casos_de_uso.perfil import (
    CasoAtualizarPerfilUsuario,
    CasoBuscarUsuarioPorAuthId,
    CasoVerificarEmailExiste,
)
from app.infraestrutura.persistencia.repositorio_usuario import RepositorioUsuarioSqlAlchemy
from kapitour_shared.autenticacao import criar_token_acesso
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_repositorio_usuario(
    sessao: Session = Depends(obter_sessao_banco),
) -> RepositorioUsuarioSqlAlchemy:
    return RepositorioUsuarioSqlAlchemy(sessao)


def obter_caso_registrar_usuario(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoRegistrarUsuario:
    return CasoRegistrarUsuario(repositorio, criar_token_acesso)


def obter_caso_entrar_usuario(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoEntrarUsuario:
    return CasoEntrarUsuario(repositorio, criar_token_acesso)


def obter_caso_buscar_usuario(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoBuscarUsuarioPorAuthId:
    return CasoBuscarUsuarioPorAuthId(repositorio)


def obter_caso_atualizar_perfil(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoAtualizarPerfilUsuario:
    return CasoAtualizarPerfilUsuario(repositorio)


def obter_caso_verificar_email(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoVerificarEmailExiste:
    return CasoVerificarEmailExiste(repositorio)
