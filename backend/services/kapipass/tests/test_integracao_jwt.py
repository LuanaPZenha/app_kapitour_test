"""Testes de integração — JWT nas listagens KapiPass."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("kapipass", __file__)

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
    par = servico_jwt.criar_par_tokens(str(uuid.uuid4()), 7, tipo_usuario_id=3)
    return par.access_token


class TestKapiPassJWT:
    def test_checkins_sem_token_401(self, cliente):
        assert cliente.get("/api/kapipass/checkins", params={"usuario_id": 7}).status_code == 401

    def test_checkins_com_token(self, cliente, token_turista):
        resposta = cliente.get(
            "/api/kapipass/checkins",
            params={"usuario_id": 7},
            headers={"Authorization": f"Bearer {token_turista}"},
        )
        assert resposta.status_code == 200

    def test_niveis_publico(self, cliente):
        assert cliente.get("/api/kapipass/niveis").status_code == 200

    def test_rankings_publico(self, cliente):
        assert cliente.get("/api/kapipass/rankings").status_code == 200
