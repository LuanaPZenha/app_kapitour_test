from fastapi import APIRouter, Depends, HTTPException

from app.apresentacao.dependencias import (
    obter_repositorio_favorito,
    obter_servico_avaliacao,
    obter_servico_favoritos,
)
from app.apresentacao.esquemas import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    AvaliacaoUpdate,
    FavoritoCreate,
    FavoritoResponse,
    PontoAvaliacaoCreate,
)
from app.infraestrutura.persistencia.repositorios import RepositorioFavorito
from app.dominio.casos_de_uso.servicos import ServicoAvaliacao, ServicoFavoritos

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "engagement"}


@roteador.get("/favoritos")
def list_favoritos(
    usuario_id: int,
    servico: ServicoFavoritos = Depends(obter_servico_favoritos),
):
    return servico.listar_com_pontos(usuario_id)


@roteador.post("/favoritos", response_model=FavoritoResponse)
def create_favorito(
    payload: FavoritoCreate,
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
):
    return repositorio.criar(payload.usuario_id, payload.ponto_id)


@roteador.delete("/favoritos")
def delete_favorito(
    usuario_id: int,
    ponto_id: int,
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
):
    ok = repositorio.excluir(usuario_id, ponto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    return {"success": True}


@roteador.get("/avaliacoes")
def list_avaliacoes(
    ponto_id: int | None = None,
    usuario_id: int | None = None,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    resultado = servico.listar(ponto_id=ponto_id, usuario_id=usuario_id)
    if usuario_id and ponto_id:
        return resultado
    if ponto_id:
        return [AvaliacaoResponse.model_validate(a) for a in resultado]
    return []


@roteador.post("/avaliacoes", response_model=AvaliacaoResponse)
def create_avaliacao(
    payload: AvaliacaoCreate,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    return servico.criar_ou_atualizar(
        payload.usuario_id, payload.ponto_id, payload.nota, payload.comentario
    )


@roteador.put("/avaliacoes/{avaliacao_id}", response_model=AvaliacaoResponse)
def update_avaliacao(
    avaliacao_id: int,
    payload: AvaliacaoUpdate,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    item = servico.atualizar_por_id(avaliacao_id, payload.nota, payload.comentario)
    if not item:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return item


@roteador.post("/ponto-avaliacoes")
def create_ponto_avaliacao(
    payload: PontoAvaliacaoCreate,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    return servico.criar_ponto_avaliacao(
        payload.ponto_id, payload.usuario_id, payload.nota, payload.comentario
    )


@roteador.get("/ponto-avaliacoes/media")
def media_ponto_avaliacoes(
    ponto_id: int,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    return servico.media_por_ponto(ponto_id)
