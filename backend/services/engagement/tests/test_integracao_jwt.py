"""Testes de integração — JWT obrigatório no engagement."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("engagement", __file__)

import pytest
from fastapi.testclient import TestClient

from app.main import app
from kapitour_shared.security.jwt_service import servico_jwt


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def token_turista():
    par = servico_jwt.criar_par_tokens(str(uuid.uuid4()), 99, tipo_usuario_id=3)
    return par.access_token


class TestEngagementJWT:
    def test_favoritos_sem_token_retorna_401(self, cliente):
        resposta = cliente.get("/api/favoritos")
        assert resposta.status_code == 401

    def test_favoritos_usuario_id_errado_retorna_403(self, cliente, token_turista):
        resposta = cliente.get(
            "/api/favoritos",
            params={"usuario_id": 1},
            headers={"Authorization": f"Bearer {token_turista}"},
        )
        assert resposta.status_code == 403

    def test_favoritos_com_token_valido(self, cliente, token_turista):
        resposta = cliente.get(
            "/api/favoritos",
            params={"usuario_id": 99},
            headers={"Authorization": f"Bearer {token_turista}"},
        )
        assert resposta.status_code == 200
        assert isinstance(resposta.json(), list)

    def test_favoritos_sem_usuario_id_usa_jwt(self, cliente, token_turista):
        resposta = cliente.get(
            "/api/favoritos",
            headers={"Authorization": f"Bearer {token_turista}"},
        )
        assert resposta.status_code == 200
        assert isinstance(resposta.json(), list)

    def test_media_avaliacoes_publica(self, cliente):
        resposta = cliente.get("/api/ponto-avaliacoes/media", params={"ponto_id": 1})
        assert resposta.status_code == 200
