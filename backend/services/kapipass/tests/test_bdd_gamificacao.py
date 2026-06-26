"""Testes BDD — microserviço KapiPass (estratégias de domínio)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("kapipass", __file__)

from pytest_bdd import given, parsers, scenarios, then, when

from app.dominio.estrategias.conquistas import REGISTRO_CRITERIOS_CONQUISTA
from app.dominio.estrategias.missoes import (
    EstrategiaMissaoCarimbos,
    EstrategiaMissaoVisitados,
)

scenarios("features/gamificacao.feature")


@given("que a missão usa estratégia de pontos visitados")
def estrategia_visitados(contexto_bdd):
    contexto_bdd["estrategia"] = EstrategiaMissaoVisitados()


@given("que a missão usa estratégia de carimbos")
def estrategia_carimbos(contexto_bdd):
    contexto_bdd["estrategia"] = EstrategiaMissaoCarimbos()


@given("que o turista visitou pelo menos 1 ponto")
def stats_um_visita(contexto_bdd):
    contexto_bdd["stats"] = {"visitados": 1, "carimbos": 0}


@given("que o turista possui apenas 2 carimbos")
def stats_dois_carimbos(contexto_bdd):
    contexto_bdd["stats"] = {"visitados": 5, "carimbos": 2}


@when(parsers.parse("calculo o progresso com {quantidade:d} visitas"))
def calcular_visitas(contexto_bdd, quantidade):
    contexto_bdd["progresso"] = contexto_bdd["estrategia"].calcular_progresso(
        {"visitados": quantidade, "carimbos": 0}
    )


@when(parsers.parse("calculo o progresso com {quantidade:d} carimbos"))
def calcular_carimbos(contexto_bdd, quantidade):
    contexto_bdd["progresso"] = contexto_bdd["estrategia"].calcular_progresso(
        {"visitados": 0, "carimbos": quantidade}
    )


@when(parsers.parse('avaliio a conquista "{codigo}"'))
@when(parsers.parse('avalio a conquista "{codigo}"'))
def avaliar_conquista(contexto_bdd, codigo):
    criterio = REGISTRO_CRITERIOS_CONQUISTA[codigo]
    contexto_bdd["atende"] = criterio.atende(contexto_bdd["stats"])


@then(parsers.parse("o progresso registrado é {valor:d}"))
def progresso_esperado(contexto_bdd, valor):
    assert contexto_bdd["progresso"] == valor


@then("o critério é atendido")
def criterio_atendido(contexto_bdd):
    assert contexto_bdd["atende"] is True


@then("o critério não é atendido")
def criterio_nao_atendido(contexto_bdd):
    assert contexto_bdd["atende"] is False
