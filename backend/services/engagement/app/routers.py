from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import Avaliacao
from app.repositories import FavoriteRepository, RatingRepository
from app.schemas import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    AvaliacaoUpdate,
    FavoritoCreate,
    FavoritoResponse,
    PontoAvaliacaoCreate,
)
from app.services import FavoriteService
from kapitour_shared.database import Base, engine, get_db

router = APIRouter()


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


@router.get("/health")
def health():
    return {"status": "ok", "service": "engagement"}


@router.get("/favoritos")
def list_favoritos(usuario_id: int, db: Session = Depends(get_db)):
    return FavoriteService(db).list_with_places(usuario_id)


@router.post("/favoritos", response_model=FavoritoResponse)
def create_favorito(payload: FavoritoCreate, db: Session = Depends(get_db)):
    return FavoriteRepository(db).create(payload.usuario_id, payload.ponto_id)


@router.delete("/favoritos")
def delete_favorito(usuario_id: int, ponto_id: int, db: Session = Depends(get_db)):
    ok = FavoriteRepository(db).delete(usuario_id, ponto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    return {"success": True}


@router.get("/avaliacoes")
def list_avaliacoes(
    ponto_id: int | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
):
    repo = RatingRepository(db)
    if usuario_id and ponto_id:
        return repo.get_user_rating(usuario_id, ponto_id)
    if ponto_id:
        return [AvaliacaoResponse.model_validate(a) for a in repo.list_by_ponto(ponto_id)]
    return []


@router.post("/avaliacoes", response_model=AvaliacaoResponse)
def create_avaliacao(payload: AvaliacaoCreate, db: Session = Depends(get_db)):
    repo = RatingRepository(db)
    existing = repo.get_user_rating(payload.usuario_id, payload.ponto_id)
    if existing:
        item = repo.update(existing, payload.nota, payload.comentario)
    else:
        item = repo.create(payload.usuario_id, payload.ponto_id, payload.nota, payload.comentario)
    return item


@router.put("/avaliacoes/{avaliacao_id}", response_model=AvaliacaoResponse)
def update_avaliacao(avaliacao_id: int, payload: AvaliacaoUpdate, db: Session = Depends(get_db)):
    avaliacao = db.query(Avaliacao).filter(Avaliacao.id == avaliacao_id).first()
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return RatingRepository(db).update(avaliacao, payload.nota, payload.comentario)


@router.post("/ponto-avaliacoes")
def create_ponto_avaliacao(payload: PontoAvaliacaoCreate, db: Session = Depends(get_db)):
    return RatingRepository(db).create_ponto_avaliacao(
        payload.ponto_id, payload.usuario_id, payload.nota, payload.comentario
    )


@router.get("/ponto-avaliacoes/media")
def media_ponto_avaliacoes(ponto_id: int, db: Session = Depends(get_db)):
    ratings = RatingRepository(db).list_ponto_avaliacoes(ponto_id)
    if not ratings:
        return {"media": 0}
    media = sum(r.nota for r in ratings) / len(ratings)
    return {"media": round(media, 1)}
