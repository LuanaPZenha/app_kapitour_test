"""Testes BDD — microserviço Content."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("content", __file__)

from pytest_bdd import given, parsers, scenarios, then, when

from app.dominio.casos_de_uso.servicos import CasoListarPontos, CasoListarRotas
from fakes.repositorios_fake import RepositorioPontoFake, RepositorioRotaFake

scenarios("features/conteudo.feature")


@given("que existem pontos cadastrados no serviço de conteúdo")
def pontos_cadastrados(contexto_bdd):
    contexto_bdd["pontos"] = RepositorioPontoFake()


@given("que existem pontos em categorias distintas")
def pontos_categorias(contexto_bdd):
    contexto_bdd["pontos"] = RepositorioPontoFake()


@given('que existe a rota "Rota Litorânea" com pontos associados')
def rota_com_pontos(contexto_bdd):
    contexto_bdd["rotas"] = CasoListarRotas(
        RepositorioRotaFake(), RepositorioPontoFake()
    )


@when("solicito a listagem de pontos")
def listar_pontos(contexto_bdd):
    caso = CasoListarPontos(contexto_bdd["pontos"])
    contexto_bdd["resultado"] = caso.listar()


@when('filtro pontos pela categoria "Praias"')
def filtrar_praias(contexto_bdd):
    caso = CasoListarPontos(contexto_bdd["pontos"])
    contexto_bdd["resultado"] = caso.listar(categoria_id=1)


@when("consulto os pontos da rota")
def pontos_da_rota(contexto_bdd):
    relacoes, ids, pontos = contexto_bdd["rotas"].pontos_da_rota(10)
    contexto_bdd["relacoes"] = relacoes
    contexto_bdd["pontos"] = pontos


@then("recebo a lista completa de pontos")
def lista_completa(contexto_bdd):
    assert len(contexto_bdd["resultado"]) == 2


@then("recebo apenas pontos dessa categoria")
def lista_filtrada(contexto_bdd):
    assert len(contexto_bdd["resultado"]) == 1
    assert contexto_bdd["resultado"][0].nome == "Praia de Itaipuaçu"


@then("recebo os pontos na ordem da rota")
def pontos_ordenados(contexto_bdd):
    assert len(contexto_bdd["pontos"]) == 2
    assert contexto_bdd["relacoes"][0].ordem == 1
