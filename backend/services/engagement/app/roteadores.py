from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modelos import Avaliacao
from app.repositorios import RepositorioAvaliacao, RepositorioFavorito
from app.esquemas import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    AvaliacaoUpdate,
    FavoritoCreate,
    FavoritoResponse,
    PontoAvaliacaoCreate,
)
from app.dependencias import obter_repositorio_favorito, obter_servico_favoritos
from app.servicos import ServicoFavoritos
from kapitour_shared.banco_dados import obter_sessao_banco

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
    sessao: Session = Depends(obter_sessao_banco),
):
    repositorio = RepositorioAvaliacao(sessao)
    if usuario_id and ponto_id:
        return repositorio.buscar_avaliacao_usuario(usuario_id, ponto_id)
    if ponto_id:
        return [AvaliacaoResponse.model_validate(a) for a in repositorio.listar_por_ponto(ponto_id)]
    return []


@roteador.post("/avaliacoes", response_model=AvaliacaoResponse)
def create_avaliacao(payload: AvaliacaoCreate, sessao: Session = Depends(obter_sessao_banco)):
    repositorio = RepositorioAvaliacao(sessao)
    existente = repositorio.buscar_avaliacao_usuario(payload.usuario_id, payload.ponto_id)
    if existente:
        item = repositorio.atualizar(existente, payload.nota, payload.comentario)
    else:
        item = repositorio.criar(payload.usuario_id, payload.ponto_id, payload.nota, payload.comentario)
    return item


@roteador.put("/avaliacoes/{avaliacao_id}", response_model=AvaliacaoResponse)
def update_avaliacao(avaliacao_id: int, payload: AvaliacaoUpdate, sessao: Session = Depends(obter_sessao_banco)):
    avaliacao = sessao.query(Avaliacao).filter(Avaliacao.id == avaliacao_id).first()
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return RepositorioAvaliacao(sessao).atualizar(avaliacao, payload.nota, payload.comentario)


@roteador.post("/ponto-avaliacoes")
def create_ponto_avaliacao(payload: PontoAvaliacaoCreate, sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioAvaliacao(sessao).criar_ponto_avaliacao(
        payload.ponto_id, payload.usuario_id, payload.nota, payload.comentario
    )


@roteador.get("/ponto-avaliacoes/media")
def media_ponto_avaliacoes(ponto_id: int, sessao: Session = Depends(obter_sessao_banco)):
    avaliacoes = RepositorioAvaliacao(sessao).listar_ponto_avaliacoes(ponto_id)
    if not avaliacoes:
        return {"media": 0}
    media = sum(a.nota for a in avaliacoes) / len(avaliacoes)
    return {"media": round(media, 1)}
