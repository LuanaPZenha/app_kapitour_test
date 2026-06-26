"""Testes BDD — microserviço Commerce."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("commerce", __file__)

from datetime import date, timedelta

from pytest_bdd import given, scenarios, then, when

from app.dominio.casos_de_uso.servicos import ServicoCupom
from app.dominio.regras.cadeia_resgate import CadeiaValidacaoResgateCupom
from app.dominio.regras.regras import (
    ValidadorCampanhaAtiva,
    ValidadorCupomDisponivel,
    ValidadorCupomExiste,
    ValidadorCupomExpirado,
    ValidadorCupomParceiro,
    ValidadorJaResgatado,
)
from fakes.repositorio_cupom_fake import RepositorioCupomFake

scenarios("features/cupons.feature")


def _criar_servico(repo: RepositorioCupomFake) -> ServicoCupom:
    cadeia = CadeiaValidacaoResgateCupom(
        [
            ValidadorJaResgatado(),
            ValidadorCupomExiste(),
            ValidadorCupomParceiro(),
            ValidadorCupomDisponivel(),
            ValidadorCupomExpirado(),
            ValidadorCampanhaAtiva(),
        ]
    )
    return ServicoCupom(repo, cadeia_validacao=cadeia)


@given("que existe um cupom válido e não resgatado")
def cupom_valido(contexto_bdd):
    repo = RepositorioCupomFake()
    repo.adicionar_cupom(1, parceiro_id=1)
    contexto_bdd["repo"] = repo
    contexto_bdd["servico"] = _criar_servico(repo)
    contexto_bdd["cupom_id"] = 1
    contexto_bdd["usuario_id"] = 100
    contexto_bdd["parceiro_id"] = 1


@given("que o usuário já resgatou o cupom")
def cupom_ja_resgatado(contexto_bdd):
    repo = RepositorioCupomFake()
    repo.adicionar_cupom(1, parceiro_id=1)
    repo.resgates.add((1, 100))
    contexto_bdd["repo"] = repo
    contexto_bdd["servico"] = _criar_servico(repo)
    contexto_bdd["cupom_id"] = 1
    contexto_bdd["usuario_id"] = 100
    contexto_bdd["parceiro_id"] = 1


@given("que o cupom está com data de validade vencida")
def cupom_expirado(contexto_bdd):
    repo = RepositorioCupomFake()
    repo.adicionar_cupom(
        2,
        parceiro_id=1,
        data_validade=date.today() - timedelta(days=1),
    )
    contexto_bdd["repo"] = repo
    contexto_bdd["servico"] = _criar_servico(repo)
    contexto_bdd["cupom_id"] = 2
    contexto_bdd["usuario_id"] = 100
    contexto_bdd["parceiro_id"] = 1


@given("que o cupom pertence a um parceiro diferente")
def cupom_outro_parceiro(contexto_bdd):
    repo = RepositorioCupomFake()
    repo.adicionar_cupom(3, parceiro_id=99)
    contexto_bdd["repo"] = repo
    contexto_bdd["servico"] = _criar_servico(repo)
    contexto_bdd["cupom_id"] = 3
    contexto_bdd["usuario_id"] = 100
    contexto_bdd["parceiro_id"] = 1


@when("o usuário resgata o cupom")
@when("tenta resgatar novamente")
@when("o usuário tenta resgatar")
@when("o usuário tenta resgatar na loja errada")
def resgatar_cupom(contexto_bdd):
    contexto_bdd["resultado"] = contexto_bdd["servico"].resgatar(
        contexto_bdd["cupom_id"],
        contexto_bdd["usuario_id"],
        contexto_bdd.get("parceiro_id"),
    )


@then("o resgate é confirmado com sucesso")
def resgate_sucesso(contexto_bdd):
    assert contexto_bdd["resultado"]["success"] is True


@then("o sistema impede o resgate duplicado")
def resgate_duplicado(contexto_bdd):
    assert contexto_bdd["resultado"]["success"] is False
    assert "já resgatado" in contexto_bdd["resultado"]["error"]


@then("o sistema informa que o cupom expirou")
def cupom_expirado_msg(contexto_bdd):
    assert contexto_bdd["resultado"]["success"] is False
    assert "expirado" in contexto_bdd["resultado"]["error"]


@then("o sistema rejeita por parceiro incorreto")
def parceiro_incorreto(contexto_bdd):
    assert contexto_bdd["resultado"]["success"] is False
    assert "parceiro" in contexto_bdd["resultado"]["error"].lower()
