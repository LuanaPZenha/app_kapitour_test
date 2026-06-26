from fastapi import Depends
from sqlalchemy.orm import Session

from app.repositorios import RepositorioFavorito
from app.servicos import ServicoFavoritos
from kapitour_shared.banco_dados import obter_sessao_banco
from kapitour_shared.clientes_http import ClienteConteudo
from kapitour_shared.contratos.clientes_http import ContratoClienteConteudo


def obter_cliente_conteudo() -> ContratoClienteConteudo:
    return ClienteConteudo()


def obter_repositorio_favorito(sessao: Session = Depends(obter_sessao_banco)) -> RepositorioFavorito:
    return RepositorioFavorito(sessao)


def obter_servico_favoritos(
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
    conteudo: ContratoClienteConteudo = Depends(obter_cliente_conteudo),
) -> ServicoFavoritos:
    return ServicoFavoritos(favoritos=repositorio, conteudo=conteudo)
