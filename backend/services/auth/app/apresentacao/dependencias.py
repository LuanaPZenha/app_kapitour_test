"""Composição de dependências — liga casos de uso à infraestrutura."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.dominio.casos_de_uso.autenticacao import (
    CasoAlterarSenha,
    CasoConfirmarEmail,
    CasoEntrarUsuario,
    CasoLogout,
    CasoRecuperarSenha,
    CasoRedefinirSenha,
    CasoRegistrarUsuario,
    CasoRenovarToken,
)
from app.dominio.casos_de_uso.perfil import (
    CasoAtualizarPerfilUsuario,
    CasoBuscarUsuarioPorAuthId,
    CasoVerificarEmailExiste,
)
from app.infraestrutura.adaptadores.gerador_token import AdaptadorGeradorToken
from app.infraestrutura.persistencia.repositorio_usuario import RepositorioUsuarioSqlAlchemy
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_repositorio_usuario(
    sessao: Session = Depends(obter_sessao_banco),
) -> RepositorioUsuarioSqlAlchemy:
    return RepositorioUsuarioSqlAlchemy(sessao)


def obter_gerador_token() -> AdaptadorGeradorToken:
    return AdaptadorGeradorToken()


def obter_caso_registrar_usuario(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
    gerador: AdaptadorGeradorToken = Depends(obter_gerador_token),
) -> CasoRegistrarUsuario:
    return CasoRegistrarUsuario(repositorio, gerador)


def obter_caso_entrar_usuario(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
    gerador: AdaptadorGeradorToken = Depends(obter_gerador_token),
) -> CasoEntrarUsuario:
    return CasoEntrarUsuario(repositorio, gerador)


def obter_caso_renovar_token(
    gerador: AdaptadorGeradorToken = Depends(obter_gerador_token),
) -> CasoRenovarToken:
    return CasoRenovarToken(gerador)


def obter_caso_logout() -> CasoLogout:
    return CasoLogout()


def obter_caso_alterar_senha(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoAlterarSenha:
    return CasoAlterarSenha(repositorio)


def obter_caso_recuperar_senha(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoRecuperarSenha:
    return CasoRecuperarSenha(repositorio)


def obter_caso_redefinir_senha(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoRedefinirSenha:
    return CasoRedefinirSenha(repositorio)


def obter_caso_confirmar_email(
    repositorio: RepositorioUsuarioSqlAlchemy = Depends(obter_repositorio_usuario),
) -> CasoConfirmarEmail:
    return CasoConfirmarEmail(repositorio)


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
