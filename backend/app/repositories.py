from datetime import date, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models import (
    Avaliacao,
    Campanha,
    Categoria,
    Cupom,
    CupomResgatado,
    Estoque,
    Favorito,
    PontoAvaliacao,
    PontoCategoria,
    PontoTuristico,
    Produto,
    Rota,
    RotaPonto,
    TipoProduto,
    Usuario,
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_auth_id(self, auth_id: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.auth_id == auth_id).first()

    def get_by_id(self, user_id: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email.lower()).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, nome: str, email: str, password: str, **kwargs) -> Usuario:
        user = Usuario(
            auth_id=str(uuid4()),
            nome=nome,
            email=email.lower(),
            senha_hash=hash_password(password),
            data_criacao=datetime.utcnow(),
            **kwargs,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: Usuario, data: dict) -> Usuario:
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Usuario | None:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.senha_hash):
            return None
        return user


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Categoria]:
        return self.db.query(Categoria).order_by(Categoria.nome).all()


class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, categoria_id: int | None = None) -> list[PontoTuristico]:
        query = self.db.query(PontoTuristico)
        if categoria_id:
            ponto_ids = [
                row.ponto_id
                for row in self.db.query(PontoCategoria)
                .filter(PontoCategoria.categoria_id == categoria_id)
                .all()
            ]
            if not ponto_ids:
                return []
            query = query.filter(PontoTuristico.id.in_(ponto_ids))
        return query.all()

    def get_by_ids(self, ids: list[int]) -> list[PontoTuristico]:
        if not ids:
            return []
        return self.db.query(PontoTuristico).filter(PontoTuristico.id.in_(ids)).all()

    def get_by_id(self, place_id: int) -> PontoTuristico | None:
        return self.db.query(PontoTuristico).filter(PontoTuristico.id == place_id).first()

    def get_ponto_categorias(self, ponto_ids: list[int]) -> list[PontoCategoria]:
        if not ponto_ids:
            return []
        return self.db.query(PontoCategoria).filter(PontoCategoria.ponto_id.in_(ponto_ids)).all()


class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Rota]:
        return self.db.query(Rota).order_by(Rota.id).all()

    def get_rota_pontos(self, rota_id: int) -> list[RotaPonto]:
        return (
            self.db.query(RotaPonto)
            .filter(RotaPonto.rota_id == rota_id)
            .order_by(RotaPonto.ordem)
            .all()
        )

    def get_rota_pontos_by_ponto_ids(self, ponto_ids: list[int]) -> list[RotaPonto]:
        if not ponto_ids:
            return []
        return self.db.query(RotaPonto).filter(RotaPonto.ponto_id.in_(ponto_ids)).all()

    def get_rotas_by_ids(self, ids: list[int]) -> list[Rota]:
        if not ids:
            return []
        return self.db.query(Rota).filter(Rota.id.in_(ids)).all()


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, usuario_id: int) -> list[Favorito]:
        return self.db.query(Favorito).filter(Favorito.usuario_id == usuario_id).all()

    def get(self, usuario_id: int, ponto_id: int) -> Favorito | None:
        return (
            self.db.query(Favorito)
            .filter(Favorito.usuario_id == usuario_id, Favorito.ponto_id == ponto_id)
            .first()
        )

    def create(self, usuario_id: int, ponto_id: int) -> Favorito:
        favorito = Favorito(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            data_adicionado=datetime.utcnow(),
        )
        self.db.add(favorito)
        self.db.commit()
        self.db.refresh(favorito)
        return favorito

    def delete(self, usuario_id: int, ponto_id: int) -> bool:
        favorito = self.get(usuario_id, ponto_id)
        if not favorito:
            return False
        self.db.delete(favorito)
        self.db.commit()
        return True


class RatingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_ponto(self, ponto_id: int) -> list[Avaliacao]:
        return self.db.query(Avaliacao).filter(Avaliacao.ponto_id == ponto_id).all()

    def get_user_rating(self, usuario_id: int, ponto_id: int) -> Avaliacao | None:
        return (
            self.db.query(Avaliacao)
            .filter(Avaliacao.usuario_id == usuario_id, Avaliacao.ponto_id == ponto_id)
            .first()
        )

    def create(self, usuario_id: int, ponto_id: int, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao = Avaliacao(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            nota=nota,
            comentario=comentario,
            data_avaliacao=datetime.utcnow(),
        )
        self.db.add(avaliacao)
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    def update(self, avaliacao: Avaliacao, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao.nota = nota
        avaliacao.comentario = comentario
        avaliacao.data_avaliacao = datetime.utcnow()
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    def create_ponto_avaliacao(
        self, ponto_id: int, usuario_id: int | None, nota: int, comentario: str | None
    ) -> PontoAvaliacao:
        item = PontoAvaliacao(
            ponto_id=ponto_id,
            usuario_id=usuario_id,
            nota=nota,
            comentario=comentario,
            data=datetime.utcnow(),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_ponto_avaliacoes(self, ponto_id: int) -> list[PontoAvaliacao]:
        return self.db.query(PontoAvaliacao).filter(PontoAvaliacao.ponto_id == ponto_id).all()


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
