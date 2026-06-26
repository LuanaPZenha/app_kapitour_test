"""Testes unitários — regras e casos de uso do microserviço Commerce."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))
from kapitour_shared.testes.bootstrap import preparar_imports

preparar_imports("commerce", __file__)

from datetime import date, timedelta
from types import SimpleNamespace

from app.dominio.regras.cadeia_resgate import CadeiaValidacaoResgateCupom
from app.dominio.regras.contexto import ContextoResgateCupom
from app.dominio.regras.regras import ValidadorCupomExpirado, ValidadorJaResgatado
from fakes.repositorio_cupom_fake import RepositorioCupomFake


class TestValidadorJaResgatado:
    def test_retorna_erro_quando_ja_resgatado(self):
        # Dado: cupom já resgatado pelo usuário
        repo = RepositorioCupomFake()
        repo.resgates.add((1, 10))
        contexto = ContextoResgateCupom(
            cupom_id=1, usuario_id=10, parceiro_id=None, repositorio=repo
        )
        validador = ValidadorJaResgatado()

        # Quando: valida resgate
        erro = validador.validar(contexto)

        # Então: retorna erro de duplicidade
        assert erro is not None
        assert erro["success"] is False


class TestValidadorCupomExpirado:
    def test_rejeita_cupom_vencido(self):
        repo = RepositorioCupomFake()
        repo.adicionar_cupom(
            1, data_validade=date.today() - timedelta(days=1)
        )
        contexto = ContextoResgateCupom(
            cupom_id=1,
            usuario_id=1,
            parceiro_id=None,
            repositorio=repo,
            cupom=repo.buscar_por_id(1),
        )
        erro = ValidadorCupomExpirado().validar(contexto)
        assert erro and "expirado" in erro["error"]


class TestCadeiaValidacao:
    def test_cadeia_para_na_primeira_falha(self):
        repo = RepositorioCupomFake()
        repo.resgates.add((5, 1))
        cadeia = CadeiaValidacaoResgateCupom([ValidadorJaResgatado()])
        contexto = ContextoResgateCupom(
            cupom_id=5, usuario_id=1, parceiro_id=None, repositorio=repo
        )
        assert cadeia.validar(contexto) is not None
