from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.apresentacao.dependencias import (
    obter_caso_atualizar_perfil,
    obter_caso_buscar_usuario,
    obter_caso_entrar_usuario,
    obter_caso_registrar_usuario,
    obter_caso_verificar_email,
    obter_repositorio_usuario,
)
from app.apresentacao.esquemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.apresentacao.mapeadores import autenticacao_para_resposta, usuario_para_resposta
from app.dominio.casos_de_uso.autenticacao import CasoEntrarUsuario, CasoRegistrarUsuario
from app.dominio.casos_de_uso.perfil import (
    CasoAtualizarPerfilUsuario,
    CasoBuscarUsuarioPorAuthId,
    CasoVerificarEmailExiste,
)
from kapitour_shared.autenticacao import (
    obter_usuario_obrigatorio_do_token,
    validar_chave_interna,
)

roteador = APIRouter()


def obter_usuario_atual(
    authorization: Annotated[str | None, Header()] = None,
    caso: CasoBuscarUsuarioPorAuthId = Depends(obter_caso_buscar_usuario),
):
    usuario_token = obter_usuario_obrigatorio_do_token(authorization)
    usuario = caso.executar(usuario_token.auth_id)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@roteador.post("/auth/register", response_model=TokenResponse)
def register(
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
        return autenticacao_para_resposta(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    caso: CasoEntrarUsuario = Depends(obter_caso_entrar_usuario),
):
    try:
        resultado = caso.executar(payload.email, payload.password)
        return autenticacao_para_resposta(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@roteador.get("/auth/me", response_model=UsuarioResponse)
def me(usuario=Depends(obter_usuario_atual)):
    return usuario_para_resposta(usuario)


@roteador.get("/usuarios/email-exists")
def email_exists(
    caso: CasoVerificarEmailExiste = Depends(obter_caso_verificar_email),
    email: str = "",
):
    return {"exists": caso.executar(email)}


@roteador.get("/usuarios/by-auth/{auth_id}", response_model=UsuarioResponse)
def get_user_by_auth(
    auth_id: str,
    caso: CasoBuscarUsuarioPorAuthId = Depends(obter_caso_buscar_usuario),
):
    usuario = caso.executar(auth_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_para_resposta(usuario)


@roteador.patch("/usuarios/{auth_id}", response_model=UsuarioResponse)
def update_user(
    auth_id: str,
    payload: UsuarioUpdateRequest,
    caso: CasoAtualizarPerfilUsuario = Depends(obter_caso_atualizar_perfil),
):
    try:
        usuario = caso.executar(auth_id, payload.model_dump(exclude_unset=True))
        return usuario_para_resposta(usuario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/internal/usuarios/{user_id}")
def internal_get_user(
    user_id: int,
    _: None = Depends(validar_chave_interna),
    repositorio=Depends(obter_repositorio_usuario),
):
    usuario = repositorio.buscar_por_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_para_resposta(usuario)


@roteador.get("/internal/usuarios/batch")
def internal_batch_users(
    ids: str = Query(...),
    _: None = Depends(validar_chave_interna),
    repositorio=Depends(obter_repositorio_usuario),
):
    ids_usuarios = [int(x) for x in ids.split(",") if x.strip()]
    usuarios = repositorio.buscar_por_ids(ids_usuarios)
    return [usuario_para_resposta(u) for u in usuarios]
