from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.modelos import PontoCategoria
from app.repositorios import RepositorioCategoria, RepositorioPonto, RepositorioRota
from app.esquemas import CategoriaResponse, PontoTuristicoResponse, RotaPontoResponse, RotaResponse
from kapitour_shared.autenticacao import validar_chave_interna
from kapitour_shared.banco_dados import obter_sessao_banco

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "content"}


@roteador.get("/categorias", response_model=list[CategoriaResponse])
def list_categorias(sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioCategoria(sessao).listar_todos()


@roteador.get("/pontos-turisticos", response_model=list[PontoTuristicoResponse])
def list_pontos(categoria_id: int | None = Query(default=None), sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioPonto(sessao).listar_todos(categoria_id)


@roteador.get("/pontos-turisticos/{ponto_id}", response_model=PontoTuristicoResponse)
def get_ponto(ponto_id: int, sessao: Session = Depends(obter_sessao_banco)):
    ponto = RepositorioPonto(sessao).buscar_por_id(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
    return ponto


@roteador.get("/internal/pontos/batch", response_model=list[PontoTuristicoResponse])
def internal_batch_pontos(
    ids: str = Query(...),
    _: None = Depends(validar_chave_interna),
    sessao: Session = Depends(obter_sessao_banco),
):
    ids_pontos = [int(x) for x in ids.split(",") if x.strip()]
    return RepositorioPonto(sessao).buscar_por_ids(ids_pontos)


@roteador.get("/ponto-categoria")
def list_ponto_categoria(
    ponto_id: int | None = None,
    categoria_id: int | None = None,
    ponto_ids: str | None = None,
    sessao: Session = Depends(obter_sessao_banco),
):
    repositorio = RepositorioPonto(sessao)
    if ponto_id:
        linhas = repositorio.buscar_ponto_categorias([ponto_id])
    elif ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        linhas = repositorio.buscar_ponto_categorias(ids)
    elif categoria_id:
        linhas = sessao.query(PontoCategoria).filter(PontoCategoria.categoria_id == categoria_id).all()
    else:
        linhas = []
    return [{"ponto_id": linha.ponto_id, "categoria_id": linha.categoria_id} for linha in linhas]


@roteador.get("/rotas", response_model=list[RotaResponse])
def list_rotas(sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioRota(sessao).listar_todos()


@roteador.get("/rotas/{rota_id}/pontos")
def rotas_pontos(rota_id: int, sessao: Session = Depends(obter_sessao_banco)):
    repositorio_rota = RepositorioRota(sessao)
    relacoes = repositorio_rota.buscar_rota_pontos(rota_id)
    ids_pontos = [r.ponto_id for r in relacoes]
    pontos = {p.id: p for p in RepositorioPonto(sessao).buscar_por_ids(ids_pontos)}
    return {
        "relacionamentos": [RotaPontoResponse.model_validate(r) for r in relacoes],
        "pontos": [
            PontoTuristicoResponse.model_validate(pontos[pid])
            for pid in ids_pontos
            if pid in pontos
        ],
    }


@roteador.get("/rota-ponto")
def list_rota_ponto(
    rota_id: int | None = None,
    ponto_ids: str | None = None,
    sessao: Session = Depends(obter_sessao_banco),
):
    repositorio = RepositorioRota(sessao)
    if rota_id:
        return [RotaPontoResponse.model_validate(r) for r in repositorio.buscar_rota_pontos(rota_id)]
    if ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        return [
            RotaPontoResponse.model_validate(r)
            for r in repositorio.buscar_rota_pontos_por_ponto_ids(ids)
        ]
    return []
