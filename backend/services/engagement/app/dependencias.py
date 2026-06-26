from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import RepositorioFavorito, RepositorioAvaliacao
from app.servicos import ServicoAvaliacao, ServicoFavoritos
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.contratos.clientes_http import ContratoClienteConteudo
from kapitour_shared.fabricas import obter_cliente_conteudo


def obter_repositorio_favorito(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioFavorito:
    return RepositorioFavorito(sessao)


def obter_repositorio_avaliacao(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioAvaliacao:
    return RepositorioAvaliacao(sessao)


def obter_servico_favoritos(
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
) -> ServicoFavoritos:
    return ServicoFavoritos(favoritos=repositorio, conteudo=conteudo)


def obter_servico_avaliacao(
    repositorio: RepositorioAvaliacao = Depends(obter_repositorio_avaliacao),
) -> ServicoAvaliacao:
    return ServicoAvaliacao(repositorio)
