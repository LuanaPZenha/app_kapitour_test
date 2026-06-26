from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Header, HTTPException
from jose import JWTError, jwt

from kapitour_shared.config import settings


@dataclass
class TokenUser:
    id: int
    auth_id: str


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(auth_id: str, user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": auth_id, "user_id": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def get_optional_token_user(
    authorization: Annotated[str | None, Header()] = None,
) -> TokenUser | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1)
    payload = decode_token(token)
    if not payload:
        return None
    auth_id = payload.get("sub")
    user_id = payload.get("user_id")
    if not auth_id or user_id is None:
        return None
    return TokenUser(id=int(user_id), auth_id=str(auth_id))


def get_required_token_user(
    authorization: Annotated[str | None, Header()] = None,
) -> TokenUser:
    user = get_optional_token_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return user


def verify_internal_key(
    x_internal_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_internal_key != settings.internal_service_key:
        raise HTTPException(status_code=403, detail="Acesso interno negado")
