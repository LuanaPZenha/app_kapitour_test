"""Testes de helpers de autenticação compartilhados."""

import pytest
from fastapi import HTTPException

from kapitour_shared.autenticacao import (
    UsuarioToken,
    exigir_permissao,
    obter_usuario_obrigatorio_do_token,
    obter_usuario_opcional_do_token,
)
from kapitour_shared.security.jwt_service import servico_jwt
from kapitour_shared.security.rbac import Role


class TestAutenticacaoHelpers:
    def _token_bearer(self, auth_id: str = "auth-1", usuario_id: int = 1, tipo: int = 3) -> str:
        par = servico_jwt.criar_par_tokens(auth_id, usuario_id, tipo)
        return f"Bearer {par.access_token}"

    def test_obter_usuario_opcional_sem_header(self):
        assert obter_usuario_opcional_do_token(None) is None

    def test_obter_usuario_opcional_com_token_valido(self):
        usuario = obter_usuario_opcional_do_token(self._token_bearer())
        assert isinstance(usuario, UsuarioToken)
        assert usuario.id == 1
        assert usuario.role == Role.TURISTA

    def test_obter_usuario_obrigatorio_sem_token(self):
        with pytest.raises(HTTPException) as exc:
            obter_usuario_obrigatorio_do_token(None)
        assert exc.value.status_code == 401

    def test_exigir_permissao_admin(self):
        verificar = exigir_permissao("usuarios:deletar")
        admin = UsuarioToken(id=1, auth_id="a", role=Role.ADMIN)
        assert verificar(admin) is admin

    def test_exigir_permissao_negada(self):
        verificar = exigir_permissao("usuarios:deletar")
        turista = UsuarioToken(id=1, auth_id="a", role=Role.TURISTA)
        with pytest.raises(HTTPException) as exc:
            verificar(turista)
        assert exc.value.status_code == 403
