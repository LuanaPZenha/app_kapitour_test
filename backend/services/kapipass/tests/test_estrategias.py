"""Testes unitários — estratégias e critérios do microserviço KapiPass."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("kapipass", __file__)

from app.dominio.estrategias.conquistas import (
    CriterioCarimbosMinimos,
    CriterioVisitadosMinimos,
    REGISTRO_CRITERIOS_CONQUISTA,
)
from app.dominio.estrategias.missoes import (
    ESTRATEGIA_MISSAO_PADRAO,
    REGISTRO_ESTRATEGIAS_MISSAO,
)


class TestEstrategiasMissao:
    def test_visitados_retorna_contagem(self):
        estrategia = REGISTRO_ESTRATEGIAS_MISSAO["visitados"]
        assert estrategia.calcular_progresso({"visitados": 3, "carimbos": 0}) == 3

    def test_padrao_usa_visitados(self):
        assert ESTRATEGIA_MISSAO_PADRAO.calcular_progresso(
            {"visitados": 2, "carimbos": 9}
        ) == 2


class TestCriteriosConquista:
    def test_explorador_marica_com_1_visita(self):
        criterio = REGISTRO_CRITERIOS_CONQUISTA["explorador_marica"]
        assert criterio.atende({"visitados": 1, "carimbos": 0}) is True

    def test_colecionador_precisa_5_carimbos(self):
        criterio = CriterioCarimbosMinimos(5)
        assert criterio.atende({"visitados": 10, "carimbos": 4}) is False
        assert criterio.atende({"visitados": 10, "carimbos": 5}) is True

    def test_visitados_minimos(self):
        criterio = CriterioVisitadosMinimos(3)
        assert criterio.atende({"visitados": 2, "carimbos": 0}) is False
