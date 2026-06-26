"""Testes unitários — casos de uso do microserviço Auth."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("auth", __file__)

import pytest

from app.dominio.casos_de_uso.autenticacao import CasoEntrarUsuario, CasoRegistrarUsuario
from app.dominio.casos_de_uso.perfil import CasoBuscarUsuarioPorAuthId
from fakes.repositorio_usuario_fake import GeradorTokenFake, RepositorioUsuarioFake


class TestCasoRegistrarUsuario:
    def test_executar_retorna_token_e_usuario(self):
        # Dado: repositório vazio e gerador de token
        repo = RepositorioUsuarioFake()
        caso = CasoRegistrarUsuario(repo, GeradorTokenFake())

        # Quando: registra novo usuário
        resultado = caso.executar(
            nome="Luana", email="luana@teste.com", password="secret"
        )

        # Então: retorna token e dados do usuário
        assert resultado.token == "token-auth-1-1"
        assert resultado.usuario.email == "luana@teste.com"

    def test_executar_rejeita_email_duplicado(self):
        repo = RepositorioUsuarioFake()
        repo.criar(nome="A", email="dup@teste.com", password="1")
        caso = CasoRegistrarUsuario(repo, GeradorTokenFake())

        with pytest.raises(ValueError, match="já está cadastrado"):
            caso.executar(nome="B", email="dup@teste.com", password="2")


class TestCasoEntrarUsuario:
    def test_executar_com_credenciais_validas(self):
        repo = RepositorioUsuarioFake()
        repo.criar(nome="Turista", email="t@teste.com", password="ok")
        caso = CasoEntrarUsuario(repo, GeradorTokenFake())

        resultado = caso.executar("t@teste.com", "ok")

        assert resultado.usuario.nome == "Turista"
        assert resultado.token.startswith("token-")


class TestCasoBuscarUsuarioPorAuthId:
    def test_executar_encontra_usuario(self):
        repo = RepositorioUsuarioFake()
        criado = repo.criar(nome="X", email="x@teste.com", password="1")
        caso = CasoBuscarUsuarioPorAuthId(repo)

        encontrado = caso.executar(criado.auth_id)

        assert encontrado is not None
        assert encontrado.id == criado.id
