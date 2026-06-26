from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas import CheckinRequest, DiarioCreate, EcoRegistrarRequest
from app.services import (
    CollectionService,
    DiaryService,
    EcoService,
    GamificationService,
    MissionService,
    RankingService,
    TreasureService,
)
from kapitour_shared.auth_tokens import TokenUser, get_required_token_user
from kapitour_shared.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "kapipass"}


@router.get("/kapipass/me")
def kapipass_me(user: TokenUser = Depends(get_required_token_user), db: Session = Depends(get_db)):
    try:
        return GamificationService(db).get_passaporte(user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/niveis")
def kapipass_niveis(db: Session = Depends(get_db)):
    return GamificationService(db).list_niveis()


@router.post("/kapipass/checkin")
def kapipass_checkin(
    payload: CheckinRequest,
    user: TokenUser = Depends(get_required_token_user),
    db: Session = Depends(get_db),
):
    try:
        return GamificationService(db).processar_checkin(
            usuario_id=user.id,
            ponto_id=payload.ponto_turistico_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/checkins")
def kapipass_checkins(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_checkins(usuario_id)


@router.get("/kapipass/carimbos")
def kapipass_carimbos(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_carimbos(usuario_id)


@router.get("/kapipass/conquistas")
def kapipass_conquistas(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_conquistas(usuario_id)


@router.get("/kapipass/colecoes")
def kapipass_colecoes(usuario_id: int, db: Session = Depends(get_db)):
    return CollectionService(db).list_colecoes(usuario_id)


@router.get("/kapipass/missoes")
def kapipass_missoes(usuario_id: int, db: Session = Depends(get_db)):
    return MissionService(db).list_missoes(usuario_id)


@router.post("/kapipass/missoes/{missao_id}/aceitar")
def kapipass_aceitar_missao(
    missao_id: int,
    user: TokenUser = Depends(get_required_token_user),
    db: Session = Depends(get_db),
):
    try:
        return MissionService(db).aceitar(user.id, missao_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/eco")
def kapipass_eco(usuario_id: int, db: Session = Depends(get_db)):
    return EcoService(db).list_atividades(usuario_id)


@router.post("/kapipass/eco/registrar")
def kapipass_eco_registrar(
    payload: EcoRegistrarRequest,
    user: TokenUser = Depends(get_required_token_user),
    db: Session = Depends(get_db),
):
    try:
        return EcoService(db).registrar(user.id, payload.eco_atividade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/diario")
def kapipass_diario(usuario_id: int, db: Session = Depends(get_db)):
    return DiaryService(db).list_entradas(usuario_id)


@router.post("/kapipass/diario")
def kapipass_diario_criar(
    payload: DiarioCreate,
    user: TokenUser = Depends(get_required_token_user),
    db: Session = Depends(get_db),
):
    return DiaryService(db).criar(
        usuario_id=user.id,
        ponto_turistico_id=payload.ponto_turistico_id,
        checkin_id=payload.checkin_id,
        comentario=payload.comentario,
        foto=payload.foto,
    )


@router.get("/kapipass/tesouros")
def kapipass_tesouros(usuario_id: int, db: Session = Depends(get_db)):
    return TreasureService(db).list_tesouros(usuario_id)


@router.post("/kapipass/tesouros/{tesouro_id}/concluir")
def kapipass_concluir_tesouro(
    tesouro_id: int,
    user: TokenUser = Depends(get_required_token_user),
    db: Session = Depends(get_db),
):
    try:
        return TreasureService(db).concluir(user.id, tesouro_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/rankings")
def kapipass_rankings(
    categoria: str = Query(default="exploradores"),
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    return RankingService(db).get_ranking(categoria, page, size)
