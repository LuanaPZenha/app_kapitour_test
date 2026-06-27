"""Testes de integração — JWT no commerce."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("commerce", __file__)

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
    par = servico_jwt.criar_par_tokens(str(uuid.uuid4()), 50, tipo_usuario_id=3)
    return par.access_token


@pytest.fixture
def token_empresa():
    par = servico_jwt.criar_par_tokens(str(uuid.uuid4()), 2, tipo_usuario_id=2)
    return par.access_token


class TestCommerceJWT:
    def test_resgatados_sem_token_401(self, cliente):
        resposta = cliente.get("/api/cupons/resgatados/50")
        assert resposta.status_code == 401

    def test_resgatados_proprio_usuario(self, cliente, token_turista):
        resposta = cliente.get(
            "/api/cupons/resgatados/50",
            headers={"Authorization": f"Bearer {token_turista}"},
        )
        assert resposta.status_code == 200
        assert resposta.json()["success"] is True

    def test_verificar_empresa_pode_consultar_turista(self, cliente, token_empresa):
        resposta = cliente.get(
            "/api/cupons/verificar",
            params={"cupom_id": 1, "usuario_id": 999},
            headers={"Authorization": f"Bearer {token_empresa}"},
        )
        assert resposta.status_code == 200

    def test_produtos_publicos(self, cliente):
        resposta = cliente.get("/api/produtos")
        assert resposta.status_code == 200

    def test_produtos_paginados(self, cliente):
        resposta = cliente.get("/api/produtos", params={"pagina": 1, "tamanho": 5})
        assert resposta.status_code == 200
        corpo = resposta.json()
        assert "itens" in corpo
        assert corpo["pagina"] == 1
        assert corpo["tamanho"] == 5

    def test_cupons_disponiveis_paginados(self, cliente):
        resposta = cliente.get("/api/cupons/disponiveis", params={"pagina": 1, "tamanho": 10})
        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["success"] is True
        assert "itens" in corpo["data"]
