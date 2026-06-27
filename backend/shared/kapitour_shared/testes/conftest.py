"""Fixtures compartilhadas para testes da infraestrutura."""

import pytest

from kapitour_shared.security.jwt_service import servico_jwt


@pytest.fixture
def par_tokens():
    return servico_jwt.criar_par_tokens("auth-test-uuid", 42, tipo_usuario_id=3)


@pytest.fixture
def headers_auth(par_tokens):
    return {"Authorization": f"Bearer {par_tokens.access_token}"}
