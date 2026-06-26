"""Testes BDD — microserviço Auth (Dado/Quando/Então)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("auth", __file__)

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.dominio.casos_de_uso.autenticacao import CasoEntrarUsuario, CasoRegistrarUsuario
from app.dominio.casos_de_uso.perfil import CasoAtualizarPerfilUsuario, CasoVerificarEmailExiste
from fakes.repositorio_usuario_fake import GeradorTokenFake, RepositorioUsuarioFake

scenarios("features/autenticacao.feature")
scenarios("features/perfil.feature")


@given(parsers.parse('que o email "{email}" não está cadastrado'))
def email_nao_cadastrado(contexto_bdd, email):
    repo = RepositorioUsuarioFake()
    contexto_bdd["repo"] = repo
    contexto_bdd["email"] = email
    contexto_bdd["gerador"] = GeradorTokenFake()


@given(parsers.parse('que o email "{email}" já está cadastrado'))
def email_ja_cadastrado(contexto_bdd, email):
    repo = RepositorioUsuarioFake()
    repo.criar(nome="Existente", email=email, password="123")
    contexto_bdd["repo"] = repo
    contexto_bdd["email"] = email
    contexto_bdd["gerador"] = GeradorTokenFake()


@given(parsers.parse('que existe um usuário com email "{email}" e senha "{senha}"'))
def usuario_existente(contexto_bdd, email, senha):
    repo = RepositorioUsuarioFake()
    repo.criar(nome="Turista", email=email, password=senha)
    contexto_bdd["repo"] = repo
    contexto_bdd["email"] = email
    contexto_bdd["senha"] = senha
    contexto_bdd["gerador"] = GeradorTokenFake()


@given("que existem dois usuários cadastrados")
def dois_usuarios(contexto_bdd):
    repo = RepositorioUsuarioFake()
    repo.criar(nome="Ana", email="ana@marica.gov.br", password="123")
    repo.criar(nome="Bruno", email="bruno@marica.gov.br", password="456")
    contexto_bdd["repo"] = repo
    contexto_bdd["gerador"] = GeradorTokenFake()


@when(parsers.parse('o usuário se registra com nome "{nome}" e senha "{senha}"'))
def registrar_usuario(contexto_bdd, nome, senha):
    caso = CasoRegistrarUsuario(contexto_bdd["repo"], contexto_bdd["gerador"])
    try:
        contexto_bdd["resultado"] = caso.executar(
            nome=nome, email=contexto_bdd["email"], password=senha
        )
        contexto_bdd["erro"] = None
    except ValueError as exc:
        contexto_bdd["erro"] = exc
        contexto_bdd["resultado"] = None


@when("o usuário tenta se registrar com o mesmo email")
def registrar_email_duplicado(contexto_bdd):
    caso = CasoRegistrarUsuario(contexto_bdd["repo"], contexto_bdd["gerador"])
    try:
        contexto_bdd["resultado"] = caso.executar(
            nome="Outro", email=contexto_bdd["email"], password="nova"
        )
        contexto_bdd["erro"] = None
    except ValueError as exc:
        contexto_bdd["erro"] = exc


@when("o usuário faz login com essas credenciais")
def login_valido(contexto_bdd):
    caso = CasoEntrarUsuario(contexto_bdd["repo"], contexto_bdd["gerador"])
    try:
        contexto_bdd["resultado"] = caso.executar(contexto_bdd["email"], contexto_bdd["senha"])
        contexto_bdd["erro"] = None
    except ValueError as exc:
        contexto_bdd["erro"] = exc


@when(parsers.parse('o usuário tenta login com senha "{senha}"'))
def login_senha(contexto_bdd, senha):
    caso = CasoEntrarUsuario(contexto_bdd["repo"], contexto_bdd["gerador"])
    try:
        contexto_bdd["resultado"] = caso.executar(contexto_bdd["email"], senha)
        contexto_bdd["erro"] = None
    except ValueError as exc:
        contexto_bdd["erro"] = exc


@when("verifico se o email existe")
def verificar_email(contexto_bdd):
    caso = CasoVerificarEmailExiste(contexto_bdd["repo"])
    contexto_bdd["email_existe"] = caso.executar(contexto_bdd["email"])


@when("o primeiro tenta usar o email do segundo")
def atualizar_email_duplicado(contexto_bdd):
    caso = CasoAtualizarPerfilUsuario(contexto_bdd["repo"])
    try:
        contexto_bdd["resultado"] = caso.executar(
            "auth-1", {"email": "bruno@marica.gov.br"}
        )
        contexto_bdd["erro"] = None
    except ValueError as exc:
        contexto_bdd["erro"] = exc


@then("o cadastro é concluído com sucesso")
def cadastro_sucesso(contexto_bdd):
    assert contexto_bdd["resultado"] is not None
    assert contexto_bdd["resultado"].usuario.email == contexto_bdd["email"]


@then("um token de acesso é emitido")
def token_emitido(contexto_bdd):
    assert contexto_bdd["resultado"].token.startswith("token-")


@then("o sistema rejeita o cadastro")
def cadastro_rejeitado(contexto_bdd):
    assert contexto_bdd["erro"] is not None


@then("informa que o email já está em uso")
def mensagem_email_duplicado(contexto_bdd):
    assert "já está cadastrado" in str(contexto_bdd["erro"])


@then("a autenticação é bem-sucedida")
def auth_sucesso(contexto_bdd):
    assert contexto_bdd["resultado"] is not None
    assert contexto_bdd["erro"] is None


@then("a autenticação é recusada")
def auth_recusada(contexto_bdd):
    assert contexto_bdd["erro"] is not None
    assert "Credenciais inválidas" in str(contexto_bdd["erro"])


@then("o sistema informa que o email está disponível")
def email_disponivel(contexto_bdd):
    assert contexto_bdd["email_existe"] is False


@then("a atualização é rejeitada")
def perfil_rejeitado(contexto_bdd):
    assert contexto_bdd["erro"] is not None
    assert "Email já cadastrado" in str(contexto_bdd["erro"])
