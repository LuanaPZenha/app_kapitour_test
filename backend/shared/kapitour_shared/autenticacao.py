from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException

from kapitour_shared.configuracao import configuracoes
from kapitour_shared.security.jwt_service import servico_jwt
from kapitour_shared.security.rbac import Role, possui_permissao, role_de_tipo_usuario


@dataclass(frozen=True)
class UsuarioToken:
    id: int
    auth_id: str
    role: Role = Role.TURISTA
    jti: str | None = None


def decodificar_token(token: str) -> dict | None:
    return servico_jwt.decodificar(token)


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

    role_str = payload.get("role")
    role = Role(role_str) if role_str else Role.TURISTA

    return UsuarioToken(
        id=int(usuario_id),
        auth_id=str(auth_id),
        role=role,
        jti=payload.get("jti"),
    )


def obter_usuario_obrigatorio_do_token(
    authorization: Annotated[str | None, Header()] = None,
) -> UsuarioToken:
    usuario = obter_usuario_opcional_do_token(authorization)
    if not usuario:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return usuario


def exigir_permissao(permissao: str):
    """Dependency factory para RBAC."""

    def _verificar(
        usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    ) -> UsuarioToken:
        if not possui_permissao(usuario.role, permissao):
            raise HTTPException(status_code=403, detail="Permissão negada")
        return usuario

    return _verificar


def validar_chave_interna(
    x_internal_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_internal_key != configuracoes.internal_service_key:
        raise HTTPException(status_code=403, detail="Acesso interno negado")


def resolver_usuario_escopo(usuario: UsuarioToken, usuario_id: int | None = None) -> int:
    """Deriva ou valida usuario_id a partir do JWT (compatível com query/body legado)."""
    if usuario_id is None:
        return usuario.id
    if usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="usuario_id não corresponde ao token")
    return usuario_id


def validar_consulta_cupom_usuario(usuario: UsuarioToken, usuario_id: int | None) -> int:
    """Empresa consulta turista (usuario_id obrigatório); demais usam o JWT."""
    if usuario.role == Role.EMPRESA:
        if usuario_id is None:
            raise HTTPException(
                status_code=400,
                detail="usuario_id é obrigatório para consulta de cupom pela empresa",
            )
        return usuario_id
    return resolver_usuario_escopo(usuario, usuario_id)


def validar_resgate_cupom(
    usuario: UsuarioToken, usuario_id: int | None, parceiro_id: int | None
) -> int:
    """Empresa resgata para turista; turista usa apenas o JWT."""
    if usuario.role == Role.EMPRESA:
        if usuario_id is None:
            raise HTTPException(
                status_code=400,
                detail="usuario_id é obrigatório para resgate pela empresa",
            )
        if parceiro_id != usuario.id:
            raise HTTPException(status_code=403, detail="parceiro_id não corresponde ao token")
        return usuario_id
    return resolver_usuario_escopo(usuario, usuario_id)


# Reexportações de compatibilidade
from kapitour_shared.security.passwords import gerar_hash_senha, senha_confere  # noqa: E402
from kapitour_shared.security.jwt_service import criar_token_acesso  # noqa: E402

__all__ = [
    "UsuarioToken",
    "criar_token_acesso",
    "decodificar_token",
    "gerar_hash_senha",
    "senha_confere",
    "obter_usuario_opcional_do_token",
    "obter_usuario_obrigatorio_do_token",
    "exigir_permissao",
    "validar_chave_interna",
    "resolver_usuario_escopo",
    "validar_consulta_cupom_usuario",
    "validar_resgate_cupom",
    "role_de_tipo_usuario",
]
