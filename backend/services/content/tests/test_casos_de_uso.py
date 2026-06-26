"""Testes unitários — microserviço Content."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("content", __file__)

from app.dominio.casos_de_uso.servicos import (
    CasoListarCategorias,
    CasoListarPontos,
    CasoListarRotas,
)
from fakes.repositorios_fake import (
    RepositorioCategoriaFake,
    RepositorioPontoFake,
    RepositorioRotaFake,
)


class TestCasoListarPontos:
    def test_buscar_por_ids_retorna_pontos_solicitados(self):
        # Dado: repositório com 2 pontos
        repo = RepositorioPontoFake()
        caso = CasoListarPontos(repo)

        # Quando: busca por ids [1, 2]
        resultado = caso.buscar_por_ids([1, 2])

        # Então: retorna ambos
        assert len(resultado) == 2
        assert {p.id for p in resultado} == {1, 2}


class TestCasoListarCategorias:
    def test_listar_retorna_categorias(self):
        caso = CasoListarCategorias(RepositorioCategoriaFake())
        assert len(caso.listar()) == 2


class TestCasoListarRotas:
    def test_listar_rota_ponto_por_ponto_ids(self):
        caso = CasoListarRotas(RepositorioRotaFake(), RepositorioPontoFake())
        relacoes = caso.listar_rota_ponto(ponto_ids=[1])
        assert len(relacoes) == 1
        assert relacoes[0].ponto_id == 1
