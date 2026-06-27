from fastapi import Depends
from sqlalchemy.orm import Session

from app.aplicacao.servicos import (
    ServicoColecao,
    ServicoDiario,
    ServicoEco,
    ServicoGamificacao,
    ServicoMissao,
    ServicoRanking,
    ServicoTesouro,
)
from app.infraestrutura.cache.servicos_cache import (
    ServicoColecaoComCache,
    ServicoDiarioComCache,
    ServicoEcoComCache,
    ServicoGamificacaoComCache,
    ServicoMissaoComCache,
    ServicoRankingComCache,
    ServicoTesouroComCache,
)
from app.infraestrutura.persistencia.repositorios import (
    RepositorioColecao,
    RepositorioDiario,
    RepositorioEco,
    RepositorioKapiPass,
    RepositorioMissao,
    RepositorioRanking,
    RepositorioTesouro,
)
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.cache.cache_service import ServicoCache
from kapitour_shared.contratos.clientes_http import (
    ContratoClienteAutenticacao,
    ContratoClienteConteudo,
)
from kapitour_shared.fabricas import obter_cliente_autenticacao, obter_cliente_conteudo


def obter_cache_kapipass() -> ServicoCache:
    return ServicoCache(prefixo="kapipass")


def obter_repositorio_kapipass(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioKapiPass:
    return RepositorioKapiPass(sessao)


def obter_repositorio_missao(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioMissao:
    return RepositorioMissao(sessao)


def obter_repositorio_diario(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioDiario:
    return RepositorioDiario(sessao)


def obter_servico_gamificacao(
    sessao: Session = Depends(obter_sessao_banco),
    kapipass: RepositorioKapiPass = Depends(obter_repositorio_kapipass),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
    autenticacao: ContratoClienteAutenticacao = Depends(obter_cliente_autenticacao),
    missoes: RepositorioMissao = Depends(obter_repositorio_missao),
    diario: RepositorioDiario = Depends(obter_repositorio_diario),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoGamificacaoComCache:
    return ServicoGamificacaoComCache(
        sessao=sessao,
        kapipass=kapipass,
        conteudo=conteudo,
        autenticacao=autenticacao,
        missoes=missoes,
        diario=diario,
        cache=cache,
    )


def obter_servico_colecao(
    sessao: Session = Depends(obter_sessao_banco),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoColecaoComCache:
    return ServicoColecaoComCache(
        sessao=sessao,
        colecoes=RepositorioColecao(sessao),
        kapipass=RepositorioKapiPass(sessao),
        conteudo=conteudo,
        cache=cache,
    )


def obter_servico_missao(
    missoes: RepositorioMissao = Depends(obter_repositorio_missao),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoMissaoComCache:
    return ServicoMissaoComCache(missoes=missoes, gamificacao=gamificacao, cache=cache)


def obter_servico_eco(
    sessao: Session = Depends(obter_sessao_banco),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoEcoComCache:
    return ServicoEcoComCache(eco=RepositorioEco(sessao), gamificacao=gamificacao, cache=cache)


def obter_servico_diario(
    diario: RepositorioDiario = Depends(obter_repositorio_diario),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoDiarioComCache:
    return ServicoDiarioComCache(diario=diario, conteudo=conteudo, cache=cache)


def obter_servico_tesouro(
    sessao: Session = Depends(obter_sessao_banco),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoTesouroComCache:
    return ServicoTesouroComCache(
        tesouros=RepositorioTesouro(sessao),
        kapipass=RepositorioKapiPass(sessao),
        gamificacao=gamificacao,
        cache=cache,
    )


def obter_servico_ranking(
    sessao: Session = Depends(obter_sessao_banco),
    autenticacao: ContratoClienteAutenticacao = Depends(obter_cliente_autenticacao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
) -> ServicoRankingComCache:
    return ServicoRankingComCache(
        rankings=RepositorioRanking(sessao), autenticacao=autenticacao, cache=cache
    )
