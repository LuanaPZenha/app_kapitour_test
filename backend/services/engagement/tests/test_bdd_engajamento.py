"""Testes BDD — microserviço Engagement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("engagement", __file__)

from pytest_bdd import given, scenarios, then, when

from app.dominio.casos_de_uso.servicos import ServicoAvaliacao, ServicoFavoritos
from fakes.repositorios_fake import (
    ClienteConteudoFake,
    RepositorioAvaliacaoFake,
    RepositorioFavoritoFake,
)

scenarios("features/engajamento.feature")


@given("que o usuário possui pontos favoritados")
def favoritos_usuario(contexto_bdd):
    contexto_bdd["servico_favoritos"] = ServicoFavoritos(
        favoritos=RepositorioFavoritoFake(),
        conteudo=ClienteConteudoFake(),
    )
    contexto_bdd["usuario_id"] = 10


@given("que um ponto possui duas avaliações")
def avaliacoes_ponto(contexto_bdd):
    repo = RepositorioAvaliacaoFake()
    repo.criar(1, 50, 4, "Bom")
    repo.criar(2, 50, 5, "Ótimo")
    contexto_bdd["servico_avaliacao"] = ServicoAvaliacao(repo)
    contexto_bdd["ponto_id"] = 50


@given("que o usuário já avaliou um ponto")
def avaliacao_existente(contexto_bdd):
    repo = RepositorioAvaliacaoFake()
    repo.criar(7, 60, 3, "Regular")
    contexto_bdd["servico_avaliacao"] = ServicoAvaliacao(repo)
    contexto_bdd["usuario_id"] = 7
    contexto_bdd["ponto_id"] = 60


@when("solicito a lista de favoritos")
def listar_favoritos(contexto_bdd):
    contexto_bdd["resultado"] = contexto_bdd["servico_favoritos"].listar_com_pontos(
        contexto_bdd["usuario_id"]
    )


@when("consulto a média do ponto")
def media_ponto(contexto_bdd):
    contexto_bdd["resultado"] = contexto_bdd["servico_avaliacao"].media_por_ponto(
        contexto_bdd["ponto_id"]
    )


@when("envia nova nota para o mesmo ponto")
def atualizar_avaliacao(contexto_bdd):
    contexto_bdd["resultado"] = contexto_bdd["servico_avaliacao"].criar_ou_atualizar(
        contexto_bdd["usuario_id"], contexto_bdd["ponto_id"], 5, "Excelente"
    )


@then("recebo cada favorito enriquecido com o ponto turístico")
def favoritos_enriquecidos(contexto_bdd):
    assert len(contexto_bdd["resultado"]) == 2
    assert contexto_bdd["resultado"][0]["pontos_turisticos"]["nome"] == "Praia"


@then("o sistema retorna a média aritmética arredondada")
def media_correta(contexto_bdd):
    assert contexto_bdd["resultado"]["media"] == 4.5


@then("a avaliação é atualizada em vez de duplicada")
def avaliacao_atualizada(contexto_bdd):
    assert contexto_bdd["resultado"].nota == 5
    repo = contexto_bdd["servico_avaliacao"]._avaliacoes
    assert len(repo._avaliacoes) == 1
