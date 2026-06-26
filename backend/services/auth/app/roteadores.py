from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.dependencias import (
    obter_repositorio_usuario,
    obter_servico_autenticacao,
    obter_servico_usuario,
)
from app.esquemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.repositorios import RepositorioUsuario
from app.servicos import ServicoAutenticacao, ServicoUsuario
from kapitour_shared.autenticacao import (
    obter_usuario_obrigatorio_do_token,
    validar_chave_interna,
)

roteador = APIRouter()


def obter_usuario_atual(
    authorization: Annotated[str | None, Header()] = None,
    repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario),
):
    usuario_token = obter_usuario_obrigatorio_do_token(authorization)
    usuario = repositorio.buscar_por_auth_id(usuario_token.auth_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@roteador.post("/auth/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    servico: ServicoAutenticacao = Depends(obter_servico_autenticacao),
):
    try:
        resultado = servico.registrar(
            nome=payload.nome,
            email=payload.email,
            password=payload.password,
            cpf=payload.cpf,
            sexo=payload.sexo,
            data_nascimento=payload.data_nascimento,
        )
        return TokenResponse(access_token=resultado["access_token"], user=resultado["user"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    servico: ServicoAutenticacao = Depends(obter_servico_autenticacao),
):
    try:
        resultado = servico.entrar(payload.email, payload.password)
        return TokenResponse(access_token=resultado["access_token"], user=resultado["user"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@roteador.get("/auth/me", response_model=UsuarioResponse)
def me(usuario=Depends(obter_usuario_atual)):
    return usuario


@roteador.get("/usuarios/email-exists")
def email_exists(repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario), email: str = ""):
    return {"exists": repositorio.email_existe(email)}


@roteador.get("/usuarios/by-auth/{auth_id}", response_model=UsuarioResponse)
def get_user_by_auth(auth_id: str, servico: ServicoUsuario = Depends(obter_servico_usuario)):
    usuario = servico.buscar_por_auth_id(auth_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@roteador.patch("/usuarios/{auth_id}", response_model=UsuarioResponse)
def update_user(
    auth_id: str,
    payload: UsuarioUpdateRequest,
    servico: ServicoUsuario = Depends(obter_servico_usuario),
):
    try:
        return servico.atualizar(auth_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/internal/usuarios/{user_id}")
def internal_get_user(
    user_id: int,
    _: None = Depends(validar_chave_interna),
    repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario),
):
    usuario = repositorio.buscar_por_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UsuarioResponse.model_validate(usuario)


@roteador.get("/internal/usuarios/batch")
def internal_batch_users(
    ids: str = Query(...),
    _: None = Depends(validar_chave_interna),
    repositorio: RepositorioUsuario = Depends(obter_repositorio_usuario),
):
    ids_usuarios = [int(x) for x in ids.split(",") if x.strip()]
    usuarios = repositorio.buscar_por_ids(ids_usuarios)
    return [UsuarioResponse.model_validate(u) for u in usuarios]
