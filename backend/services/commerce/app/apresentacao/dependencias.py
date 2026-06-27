from fastapi import Depends
from sqlalchemy.orm import Session

from app.dominio.regras import (
    CadeiaValidacaoResgateCupom,
    ValidadorCampanhaAtiva,
    ValidadorCupomDisponivel,
    ValidadorCupomExiste,
    ValidadorCupomExpirado,
    ValidadorCupomParceiro,
    ValidadorJaResgatado,
)
from app.infraestrutura.cache.servicos_cache import RepositorioLojaComCache, ServicoCupomComCache
from app.infraestrutura.persistencia.repositorios import RepositorioCupom, RepositorioLoja
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.cache.cache_service import ServicoCache


def obter_cache_commerce() -> ServicoCache:
    return ServicoCache(prefixo="commerce")


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


def obter_repositorio_loja(
    sessao: Session = Depends(obter_sessao_banco),
    cache: ServicoCache = Depends(obter_cache_commerce),
) -> RepositorioLojaComCache:
    return RepositorioLojaComCache(RepositorioLoja(sessao), cache=cache)


def obter_servico_cupom(
    repositorio: RepositorioCupom = Depends(obter_repositorio_cupom),
    cadeia: CadeiaValidacaoResgateCupom = Depends(obter_cadeia_validacao_resgate),
    cache: ServicoCache = Depends(obter_cache_commerce),
) -> ServicoCupomComCache:
    return ServicoCupomComCache(repositorio=repositorio, cadeia_validacao=cadeia, cache=cache)
