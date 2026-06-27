"""Testes de integração do serviço de autenticação."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("auth", __file__)

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


class TestAuthEndpoints:
    def test_health(self, cliente):
        resposta = cliente.get("/api/health")
        assert resposta.status_code == 200
        assert resposta.json()["service"] == "auth"

    def test_register_e_login(self, cliente):
        import uuid

        email = f"user_{uuid.uuid4().hex[:8]}@teste.com"
        registro = cliente.post(
            "/api/auth/register",
            json={"nome": "Novo", "email": email, "password": "senha123"},
        )
        assert registro.status_code == 200
        dados = registro.json()
        assert "access_token" in dados
        assert dados["token_type"] == "bearer"
        assert dados["user"]["email"] == email

        login = cliente.post(
            "/api/auth/login",
            json={"email": email, "password": "senha123"},
        )
        assert login.status_code == 200
        assert login.json()["access_token"]

    def test_me_requer_autenticacao(self, cliente):
        resposta = cliente.get("/api/auth/me")
        assert resposta.status_code == 401

    def test_refresh_token_invalido(self, cliente):
        resposta = cliente.post(
            "/api/auth/refresh",
            json={"refresh_token": "token-invalido"},
        )
        assert resposta.status_code == 401
