from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.repositories import UserRepository
from app.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.services import AuthService, UserService
from kapitour_shared.auth_tokens import get_required_token_user, verify_internal_key
from kapitour_shared.database import get_db

router = APIRouter()


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):
    token_user = get_required_token_user(authorization)
    user = UserRepository(db).get_by_auth_id(token_user.auth_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


@router.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).register(
            nome=payload.nome,
            email=payload.email,
            password=payload.password,
            cpf=payload.cpf,
            sexo=payload.sexo,
            data_nascimento=payload.data_nascimento,
        )
        return TokenResponse(access_token=result["access_token"], user=result["user"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).login(payload.email, payload.password)
        return TokenResponse(access_token=result["access_token"], user=result["user"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/auth/me", response_model=UsuarioResponse)
def me(user=Depends(get_current_user)):
    return user


@router.get("/usuarios/email-exists")
def email_exists(email: str, db: Session = Depends(get_db)):
    return {"exists": UserRepository(db).email_exists(email)}


@router.get("/usuarios/by-auth/{auth_id}", response_model=UsuarioResponse)
def get_user_by_auth(auth_id: str, db: Session = Depends(get_db)):
    user = UserService(db).get_by_auth_id(auth_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.patch("/usuarios/{auth_id}", response_model=UsuarioResponse)
def update_user(auth_id: str, payload: UsuarioUpdateRequest, db: Session = Depends(get_db)):
    try:
        return UserService(db).update(auth_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/internal/usuarios/{user_id}")
def internal_get_user(
    user_id: int,
    _: None = Depends(verify_internal_key),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UsuarioResponse.model_validate(user)


@router.get("/internal/usuarios/batch")
def internal_batch_users(
    ids: str = Query(...),
    _: None = Depends(verify_internal_key),
    db: Session = Depends(get_db),
):
    user_ids = [int(x) for x in ids.split(",") if x.strip()]
    users = UserRepository(db).get_by_ids(user_ids)
    return [UsuarioResponse.model_validate(u) for u in users]
