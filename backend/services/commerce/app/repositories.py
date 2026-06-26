from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Campanha, Cupom, CupomResgatado, Estoque, Produto, TipoProduto


class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_produtos(self) -> list[Produto]:
        return self.db.query(Produto).all()

    def list_tipos(self) -> list[TipoProduto]:
        return self.db.query(TipoProduto).all()

    def list_estoque(self) -> list[Estoque]:
        return self.db.query(Estoque).all()


class CouponRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_available(self, parceiro_id: int | None = None) -> list[Cupom]:
        query = self.db.query(Cupom).filter(Cupom.quantidade_disponivel > 0)
        if parceiro_id:
            query = query.filter(Cupom.parceiro_id == parceiro_id)
        return query.all()

    def get_by_id(self, cupom_id: int) -> Cupom | None:
        return self.db.query(Cupom).filter(Cupom.id == cupom_id).first()

    def get_campanha(self, campanha_id: int) -> Campanha | None:
        return self.db.query(Campanha).filter(Campanha.id == campanha_id).first()

    def list_resgatados(self, usuario_id: int) -> list[CupomResgatado]:
        return self.db.query(CupomResgatado).filter(CupomResgatado.usuario_id == usuario_id).all()

    def already_redeemed(self, cupom_id: int, usuario_id: int) -> bool:
        return (
            self.db.query(CupomResgatado)
            .filter(
                CupomResgatado.cupom_id == cupom_id,
                CupomResgatado.usuario_id == usuario_id,
            )
            .first()
            is not None
        )

    def redeem(self, cupom: Cupom, usuario_id: int) -> CupomResgatado:
        resgate = CupomResgatado(
            cupom_id=cupom.id,
            usuario_id=usuario_id,
            data_resgate=datetime.utcnow(),
        )
        cupom.quantidade_disponivel -= 1
        self.db.add(resgate)
        self.db.commit()
        self.db.refresh(resgate)
        return resgate

    def list_by_parceiro(self, parceiro_id: int) -> list[Cupom]:
        return self.db.query(Cupom).filter(Cupom.parceiro_id == parceiro_id).all()
