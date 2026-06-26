"""Testes unitários — microserviço Engagement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("engagement", __file__)

from app.dominio.casos_de_uso.servicos import ServicoAvaliacao, ServicoFavoritos
from fakes.repositorios_fake import (
    ClienteConteudoFake,
    RepositorioAvaliacaoFake,
    RepositorioFavoritoFake,
)


class TestServicoFavoritos:
    def test_listar_com_pontos_monta_payload(self):
        servico = ServicoFavoritos(
            favoritos=RepositorioFavoritoFake(),
            conteudo=ClienteConteudoFake(),
        )
        resultado = servico.listar_com_pontos(10)
        assert all("pontos_turisticos" in item for item in resultado)


class TestServicoAvaliacao:
    def test_media_zero_sem_avaliacoes(self):
        servico = ServicoAvaliacao(RepositorioAvaliacaoFake())
        assert servico.media_por_ponto(999)["media"] == 0

    def test_criar_ou_atualizar_nao_duplica(self):
        repo = RepositorioAvaliacaoFake()
        servico = ServicoAvaliacao(repo)
        servico.criar_ou_atualizar(1, 5, 4, "A")
        servico.criar_ou_atualizar(1, 5, 5, "B")
        assert len(repo._avaliacoes) == 1
        assert repo._avaliacoes[0].nota == 5
