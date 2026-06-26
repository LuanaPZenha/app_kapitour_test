from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import PontoCategoria
from app.repositories import CategoryRepository, PlaceRepository, RouteRepository
from app.schemas import CategoriaResponse, PontoTuristicoResponse, RotaPontoResponse, RotaResponse
from kapitour_shared.auth_tokens import verify_internal_key
from kapitour_shared.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "content"}


@router.get("/categorias", response_model=list[CategoriaResponse])
def list_categorias(db: Session = Depends(get_db)):
    return CategoryRepository(db).list_all()


@router.get("/pontos-turisticos", response_model=list[PontoTuristicoResponse])
def list_pontos(categoria_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    return PlaceRepository(db).list_all(categoria_id)


@router.get("/pontos-turisticos/{ponto_id}", response_model=PontoTuristicoResponse)
def get_ponto(ponto_id: int, db: Session = Depends(get_db)):
    ponto = PlaceRepository(db).get_by_id(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
    return ponto


@router.get("/internal/pontos/batch", response_model=list[PontoTuristicoResponse])
def internal_batch_pontos(
    ids: str = Query(...),
    _: None = Depends(verify_internal_key),
    db: Session = Depends(get_db),
):
    ponto_ids = [int(x) for x in ids.split(",") if x.strip()]
    return PlaceRepository(db).get_by_ids(ponto_ids)


@router.get("/ponto-categoria")
def list_ponto_categoria(
    ponto_id: int | None = None,
    categoria_id: int | None = None,
    ponto_ids: str | None = None,
    db: Session = Depends(get_db),
):
    repo = PlaceRepository(db)
    if ponto_id:
        rows = repo.get_ponto_categorias([ponto_id])
    elif ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        rows = repo.get_ponto_categorias(ids)
    elif categoria_id:
        rows = db.query(PontoCategoria).filter(PontoCategoria.categoria_id == categoria_id).all()
    else:
        rows = []
    return [{"ponto_id": row.ponto_id, "categoria_id": row.categoria_id} for row in rows]


@router.get("/rotas", response_model=list[RotaResponse])
def list_rotas(db: Session = Depends(get_db)):
    return RouteRepository(db).list_all()


@router.get("/rotas/{rota_id}/pontos")
def rotas_pontos(rota_id: int, db: Session = Depends(get_db)):
    repo = RouteRepository(db)
    rels = repo.get_rota_pontos(rota_id)
    ponto_ids = [r.ponto_id for r in rels]
    pontos = {p.id: p for p in PlaceRepository(db).get_by_ids(ponto_ids)}
    return {
        "relacionamentos": [RotaPontoResponse.model_validate(r) for r in rels],
        "pontos": [PontoTuristicoResponse.model_validate(pontos[pid]) for pid in ponto_ids if pid in pontos],
    }


@router.get("/rota-ponto")
def list_rota_ponto(
    rota_id: int | None = None,
    ponto_ids: str | None = None,
    db: Session = Depends(get_db),
):
    repo = RouteRepository(db)
    if rota_id:
        return [RotaPontoResponse.model_validate(r) for r in repo.get_rota_pontos(rota_id)]
    if ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        return [RotaPontoResponse.model_validate(r) for r in repo.get_rota_pontos_by_ponto_ids(ids)]
    return []
