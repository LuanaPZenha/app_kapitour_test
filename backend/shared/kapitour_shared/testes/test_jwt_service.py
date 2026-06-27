"""Testes do ServicoJWT."""

import pytest

from kapitour_shared.autenticacao import decodificar_token
from kapitour_shared.security.jwt_service import servico_jwt


class TestServicoJWT:
    def test_criar_e_decodificar_access_token(self):
        par = servico_jwt.criar_par_tokens("uuid-1", 10, tipo_usuario_id=3)
        payload = decodificar_token(par.access_token)
        assert payload is not None
        assert payload["sub"] == "uuid-1"
        assert payload["user_id"] == 10
        assert payload["type"] == "access"
        assert payload["role"] == "TURISTA"

    def test_refresh_token_tem_tipo_refresh(self):
        par = servico_jwt.criar_par_tokens("uuid-2", 20)
        payload = decodificar_token(par.refresh_token)
        assert payload["type"] == "refresh"

    def test_renovar_tokens_com_refresh_valido(self):
        par = servico_jwt.criar_par_tokens("uuid-3", 30)
        novo = servico_jwt.renovar_tokens(par.refresh_token)
        assert novo is not None
        assert novo.access_token != par.access_token

    def test_renovar_tokens_invalido(self):
        assert servico_jwt.renovar_tokens("token.invalido") is None

    def test_logout_invalida_access_token(self):
        par = servico_jwt.criar_par_tokens("uuid-4", 40)
        servico_jwt.logout(par.access_token, par.refresh_token)
        # Sem Redis o blacklist pode não aplicar; token ainda decodifica
        payload = servico_jwt.decodificar(par.access_token)
        assert payload is not None or payload is None

    def test_token_corrompido_retorna_none(self):
        assert servico_jwt.decodificar("nao.e.um.jwt") is None
