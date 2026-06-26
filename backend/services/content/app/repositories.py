from sqlalchemy.orm import Session

from app.models import Categoria, PontoCategoria, PontoTuristico, Rota, RotaPonto


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
