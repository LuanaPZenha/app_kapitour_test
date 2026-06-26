from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import (
    RepositorioColecao,
    RepositorioDiario,
    RepositorioEco,
    RepositorioKapiPass,
    RepositorioMissao,
    RepositorioRanking,
    RepositorioTesouro,
)
from app.servicos import (
    ServicoColecao,
    ServicoDiario,
    ServicoEco,
    ServicoGamificacao,
    ServicoMissao,
    ServicoRanking,
    ServicoTesouro,
)
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.clientes_http import ClienteAutenticacao, ClienteConteudo
from kapitour_shared.contratos.clientes_http import (
    ContratoClienteAutenticacao,
    ContratoClienteConteudo,
)


def obter_cliente_conteudo() -> ContratoClienteConteudo:
    return ClienteConteudo()


def obter_cliente_autenticacao() -> ContratoClienteAutenticacao:
    return ClienteAutenticacao()


def obter_repositorio_kapipass(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioKapiPass:
    return RepositorioKapiPass(sessao)


def obter_servico_gamificacao(
    sessao: Session = Depends(obter_sessao_banco),
    kapipass: RepositorioKapiPass = Depends(obter_repositorio_kapipass),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
    autenticacao: ContratoClienteAutenticacao = Depends(obter_cliente_autenticacao),
) -> ServicoGamificacao:
    return ServicoGamificacao(
        sessao=sessao,
        kapipass=kapipass,
        conteudo=conteudo,
        autenticacao=autenticacao,
        missoes=RepositorioMissao(sessao),
        diario=RepositorioDiario(sessao),
    )


def obter_servico_colecao(
    sessao: Session = Depends(obter_sessao_banco),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
) -> ServicoColecao:
    return ServicoColecao(
        sessao=sessao,
        colecoes=RepositorioColecao(sessao),
        kapipass=RepositorioKapiPass(sessao),
        conteudo=conteudo,
    )


def obter_servico_missao(
    sessao: Session = Depends(obter_sessao_banco),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
) -> ServicoMissao:
    return ServicoMissao(
        missoes=RepositorioMissao(sessao),
        gamificacao=gamificacao,
    )


def obter_servico_eco(
    sessao: Session = Depends(obter_sessao_banco),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
) -> ServicoEco:
    return ServicoEco(
        eco=RepositorioEco(sessao),
        gamificacao=gamificacao,
    )


def obter_servico_diario(
    sessao: Session = Depends(obter_sessao_banco),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
) -> ServicoDiario:
    return ServicoDiario(
        diario=RepositorioDiario(sessao),
        conteudo=conteudo,
    )


def obter_servico_tesouro(
    sessao: Session = Depends(obter_sessao_banco),
    gamificacao: ServicoGamificacao = Depends(obter_servico_gamificacao),
) -> ServicoTesouro:
    return ServicoTesouro(
        tesouros=RepositorioTesouro(sessao),
        kapipass=RepositorioKapiPass(sessao),
        gamificacao=gamificacao,
    )


def obter_servico_ranking(
    sessao: Session = Depends(obter_sessao_banco),
    autenticacao: ContratoClienteAutenticacao = Depends(obter_cliente_autenticacao),
) -> ServicoRanking:
    return ServicoRanking(
        rankings=RepositorioRanking(sessao),
        autenticacao=autenticacao,
    )
