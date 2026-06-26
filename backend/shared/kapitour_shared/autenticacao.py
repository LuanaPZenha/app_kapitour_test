from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Header, HTTPException
from jose import JWTError, jwt

from kapitour_shared.configuracao import configuracoes


@dataclass(frozen=True)
class UsuarioToken:
    id: int
    auth_id: str


def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def senha_confere(senha_informada: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha_informada.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )


def criar_token_acesso(auth_id: str, usuario_id: int) -> str:
    expira_em = datetime.utcnow() + timedelta(minutes=configuracoes.jwt_expire_minutes)
    payload = {"sub": auth_id, "user_id": usuario_id, "exp": expira_em}
    return jwt.encode(payload, configuracoes.jwt_secret, algorithm=configuracoes.jwt_algorithm)


def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            configuracoes.jwt_secret,
            algorithms=[configuracoes.jwt_algorithm],
        )
    except JWTError:
        return None


def _extrair_token_do_cabecalho(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.replace("Bearer ", "", 1)


def obter_usuario_opcional_do_token(
    authorization: Annotated[str | None, Header()] = None,
) -> UsuarioToken | None:
    token = _extrair_token_do_cabecalho(authorization)
    if not token:
        return None

    payload = decodificar_token(token)
    if not payload:
        return None

    auth_id = payload.get("sub")
    usuario_id = payload.get("user_id")
    if not auth_id or usuario_id is None:
        return None

    return UsuarioToken(id=int(usuario_id), auth_id=str(auth_id))


def obter_usuario_obrigatorio_do_token(
    authorization: Annotated[str | None, Header()] = None,
) -> UsuarioToken:
    usuario = obter_usuario_opcional_do_token(authorization)
    if not usuario:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return usuario


def validar_chave_interna(
    x_internal_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_internal_key != configuracoes.internal_service_key:
        raise HTTPException(status_code=403, detail="Acesso interno negado")
