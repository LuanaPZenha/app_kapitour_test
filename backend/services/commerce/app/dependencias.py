from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import RepositorioCupom
from app.servicos import ServicoCupom
from app.validadores import (
    CadeiaValidacaoResgateCupom,
    ValidadorCampanhaAtiva,
    ValidadorCupomDisponivel,
    ValidadorCupomExiste,
    ValidadorCupomExpirado,
    ValidadorCupomParceiro,
    ValidadorJaResgatado,
)
from kapitour_shared.banco_dados import obter_sessao_banco


def obter_cadeia_validacao_resgate() -> CadeiaValidacaoResgateCupom:
    return CadeiaValidacaoResgateCupom(
        [
            ValidadorJaResgatado(),
            ValidadorCupomExiste(),
            ValidadorCupomParceiro(),
            ValidadorCupomDisponivel(),
            ValidadorCupomExpirado(),
            ValidadorCampanhaAtiva(),
        ]
    )


def obter_repositorio_cupom(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioCupom:
    return RepositorioCupom(sessao)


def obter_servico_cupom(
    repositorio: RepositorioCupom = Depends(obter_repositorio_cupom),
    cadeia: CadeiaValidacaoResgateCupom = Depends(obter_cadeia_validacao_resgate),
) -> ServicoCupom:
    return ServicoCupom(repositorio=repositorio, cadeia_validacao=cadeia)
