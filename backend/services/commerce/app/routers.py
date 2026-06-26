from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.repositories import CouponRepository, StoreRepository
from app.schemas import CupomResgateRequest, EstoqueResponse, ProdutoResponse, TipoProdutoResponse
from app.services import CouponService
from kapitour_shared.database import get_db

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "commerce"}


@router.get("/produtos", response_model=list[ProdutoResponse])
def list_produtos(db: Session = Depends(get_db)):
    return StoreRepository(db).list_produtos()


@router.get("/tipos-produto", response_model=list[TipoProdutoResponse])
def list_tipos_produto(db: Session = Depends(get_db)):
    return StoreRepository(db).list_tipos()


@router.get("/estoque", response_model=list[EstoqueResponse])
def list_estoque(db: Session = Depends(get_db)):
    return StoreRepository(db).list_estoque()


@router.get("/cupons/disponiveis")
def cupons_disponiveis(parceiro_id: int | None = None, db: Session = Depends(get_db)):
    data = CouponService(db).list_available(parceiro_id)
    return {"success": True, "data": data}


@router.get("/cupons/resgatados/{usuario_id}")
def cupons_resgatados(usuario_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).list_resgatados(usuario_id)
    return {"success": True, "data": data}


@router.get("/cupons/verificar")
def verificar_cupom(cupom_id: int, usuario_id: int, db: Session = Depends(get_db)):
    ja = CouponRepository(db).already_redeemed(cupom_id, usuario_id)
    return {"success": True, "jaResgatado": ja}


@router.post("/cupons/resgatar")
def resgatar_cupom(payload: CupomResgateRequest, db: Session = Depends(get_db)):
    return CouponService(db).redeem(payload.cupom_id, payload.usuario_id, payload.parceiro_id)


@router.get("/cupons/campanhas-parceiro/{parceiro_id}")
def campanhas_parceiro(parceiro_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).campanhas_parceiro(parceiro_id)
    return {"success": True, "data": data}


@router.get("/cupons/contagem-campanha/{parceiro_id}")
def contagem_campanha(parceiro_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).contagem_por_campanha(parceiro_id)
    return {"success": True, "data": data}
