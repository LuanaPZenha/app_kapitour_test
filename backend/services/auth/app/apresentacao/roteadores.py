from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from app.apresentacao.dependencias import (
    obter_caso_alterar_senha,
    obter_caso_atualizar_perfil,
    obter_caso_buscar_usuario,
    obter_caso_confirmar_email,
    obter_caso_entrar_usuario,
    obter_caso_logout,
    obter_caso_recuperar_senha,
    obter_caso_redefinir_senha,
    obter_caso_registrar_usuario,
    obter_caso_renovar_token,
    obter_caso_verificar_email,
    obter_repositorio_usuario,
)
from app.apresentacao.esquemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.apresentacao.mapeadores import autenticacao_para_resposta, usuario_para_resposta
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
from kapitour_shared.autenticacao import (
    obter_usuario_obrigatorio_do_token,
    validar_chave_interna,
)
from kapitour_shared.events.audit import registrar_evento_auditoria

roteador = APIRouter()


def obter_usuario_atual(
    authorization: Annotated[str | None, Header()] = None,
    caso: CasoBuscarUsuarioPorAuthId = Depends(obter_caso_buscar_usuario),
):
    usuario_token = obter_usuario_obrigatorio_do_token(authorization)
    usuario = caso.executar(usuario_token.auth_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario, usuario_token


@roteador.post(
    "/auth/register",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Cadastrar novo usuário",
    responses={400: {"description": "E-mail já cadastrado ou dados inválidos"}},
)
def register(
    request: Request,
    payload: RegisterRequest,
    caso: CasoRegistrarUsuario = Depends(obter_caso_registrar_usuario),
):
    try:
        resultado = caso.executar(
            nome=payload.nome,
            email=payload.email,
            password=payload.password,
            cpf=payload.cpf,
            sexo=payload.sexo,
            data_nascimento=payload.data_nascimento,
        )
        registrar_evento_auditoria(
            "cadastro",
            usuario_id=resultado.usuario.id,
            auth_id=resultado.usuario.auth_id,
            ip=request.client.host if request.client else None,
            request_id=getattr(request.state, "request_id", None),
        )
        return autenticacao_para_resposta(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Autenticar com e-mail e senha",
    responses={401: {"description": "Credenciais inválidas"}},
)
def login(
    request: Request,
    payload: LoginRequest,
    caso: CasoEntrarUsuario = Depends(obter_caso_entrar_usuario),
):
    try:
        resultado = caso.executar(payload.email, payload.password)
        registrar_evento_auditoria(
            "login",
            usuario_id=resultado.usuario.id,
            auth_id=resultado.usuario.auth_id,
            ip=request.client.host if request.client else None,
            request_id=getattr(request.state, "request_id", None),
        )
        return autenticacao_para_resposta(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@roteador.post(
    "/auth/refresh",
    response_model=RefreshTokenResponse,
    tags=["auth"],
    summary="Renovar access token",
    responses={401: {"description": "Refresh token inválido ou expirado"}},
)
def refresh_token(
    payload: RefreshTokenRequest,
    caso: CasoRenovarToken = Depends(obter_caso_renovar_token),
):
    par = caso.executar(payload.refresh_token)
    if not par:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")
    access, refresh = par
    return RefreshTokenResponse(access_token=access, refresh_token=refresh)


@roteador.post(
    "/auth/logout",
    tags=["auth"],
    summary="Encerrar sessão e invalidar tokens",
    status_code=204,
)
def logout(
    request: Request,
    payload: LogoutRequest,
    authorization: Annotated[str | None, Header()] = None,
    caso: CasoLogout = Depends(obter_caso_logout),
):
    from kapitour_shared.autenticacao import decodificar_token

    access = authorization.replace("Bearer ", "", 1) if authorization else None
    payload_audit = decodificar_token(access) if access else None
    caso.executar(access, payload.refresh_token)
    registrar_evento_auditoria(
        "logout",
        usuario_id=payload_audit.get("user_id") if payload_audit else None,
        auth_id=payload_audit.get("sub") if payload_audit else None,
        ip=request.client.host if request.client else None,
        request_id=getattr(request.state, "request_id", None),
    )


@roteador.get(
    "/auth/me",
    response_model=UsuarioResponse,
    tags=["auth"],
    summary="Perfil do usuário autenticado",
)
def me(dados=Depends(obter_usuario_atual)):
    usuario, _ = dados
    return usuario_para_resposta(usuario)


@roteador.post(
    "/auth/change-password",
    tags=["auth"],
    summary="Alterar senha do usuário autenticado",
    status_code=204,
)
def change_password(
    payload: ChangePasswordRequest,
    dados=Depends(obter_usuario_atual),
    caso: CasoAlterarSenha = Depends(obter_caso_alterar_senha),
):
    usuario, _ = dados
    try:
        caso.executar(usuario.auth_id, payload.senha_atual, payload.nova_senha)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.post(
    "/auth/forgot-password",
    tags=["auth"],
    summary="Solicitar recuperação de senha",
    status_code=202,
)
def forgot_password(
    payload: ForgotPasswordRequest,
    caso: CasoRecuperarSenha = Depends(obter_caso_recuperar_senha),
):
    caso.executar(payload.email)
    return {"message": "Se o e-mail existir, instruções foram enviadas."}


@roteador.post(
    "/auth/reset-password",
    tags=["auth"],
    summary="Redefinir senha com token",
    status_code=204,
)
def reset_password(
    payload: ResetPasswordRequest,
    caso: CasoRedefinirSenha = Depends(obter_caso_redefinir_senha),
):
    try:
        caso.executar(payload.token, payload.nova_senha)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get(
    "/auth/verify-email",
    tags=["auth"],
    summary="Confirmar e-mail com token",
)
def verify_email(
    token: str = Query(...),
    caso: CasoConfirmarEmail = Depends(obter_caso_confirmar_email),
):
    try:
        caso.executar(token)
        return {"message": "E-mail confirmado com sucesso."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/usuarios/email-exists", tags=["usuarios"], summary="Verificar se e-mail existe")
def email_exists(
    caso: CasoVerificarEmailExiste = Depends(obter_caso_verificar_email),
    email: str = "",
):
    return {"exists": caso.executar(email)}


@roteador.get(
    "/usuarios/by-auth/{auth_id}",
    response_model=UsuarioResponse,
    tags=["usuarios"],
    summary="Buscar usuário por auth_id",
)
def get_user_by_auth(
    auth_id: str,
    authorization: Annotated[str | None, Header()] = None,
    caso: CasoBuscarUsuarioPorAuthId = Depends(obter_caso_buscar_usuario),
):
    from kapitour_shared.autenticacao import obter_usuario_opcional_do_token

    usuario_token = obter_usuario_opcional_do_token(authorization)
    if usuario_token and usuario_token.auth_id != auth_id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    usuario = caso.executar(auth_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_para_resposta(usuario)


@roteador.patch(
    "/usuarios/{auth_id}",
    response_model=UsuarioResponse,
    tags=["usuarios"],
    summary="Atualizar perfil do usuário",
)
def update_user(
    request: Request,
    auth_id: str,
    payload: UsuarioUpdateRequest,
    dados=Depends(obter_usuario_atual),
    caso: CasoAtualizarPerfilUsuario = Depends(obter_caso_atualizar_perfil),
):
    _, usuario_token = dados
    if usuario_token.auth_id != auth_id:
        raise HTTPException(status_code=403, detail="Não autorizado a alterar este perfil")
    try:
        usuario = caso.executar(auth_id, payload.model_dump(exclude_unset=True))
        registrar_evento_auditoria(
            "alteracao_perfil",
            usuario_id=usuario.id,
            auth_id=auth_id,
            ip=request.client.host if request.client else None,
            request_id=getattr(request.state, "request_id", None),
        )
        return usuario_para_resposta(usuario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/internal/usuarios/{user_id}", include_in_schema=False)
def internal_get_user(
    user_id: int,
    _: None = Depends(validar_chave_interna),
    repositorio=Depends(obter_repositorio_usuario),
):
    usuario = repositorio.buscar_por_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_para_resposta(usuario)


@roteador.get("/internal/usuarios/batch", include_in_schema=False)
def internal_batch_users(
    ids: str = Query(...),
    _: None = Depends(validar_chave_interna),
    repositorio=Depends(obter_repositorio_usuario),
):
    ids_usuarios = [int(x) for x in ids.split(",") if x.strip()]
    usuarios = repositorio.buscar_por_ids(ids_usuarios)
    return [usuario_para_resposta(u) for u in usuarios]
