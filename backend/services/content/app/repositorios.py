from sqlalchemy.orm import Session

from app.modelos import Categoria, PontoCategoria, PontoTuristico, Rota, RotaPonto


class RepositorioCategoria:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self) -> list[Categoria]:
        return self.sessao.query(Categoria).order_by(Categoria.nome).all()


class RepositorioPonto:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self, categoria_id: int | None = None) -> list[PontoTuristico]:
        consulta = self.sessao.query(PontoTuristico)
        if categoria_id:
            ids_pontos = self._buscar_ids_por_categoria(categoria_id)
            if not ids_pontos:
                return []
            consulta = consulta.filter(PontoTuristico.id.in_(ids_pontos))
        return consulta.all()

    def _buscar_ids_por_categoria(self, categoria_id: int) -> list[int]:
        return [
            linha.ponto_id
            for linha in self.sessao.query(PontoCategoria)
            .filter(PontoCategoria.categoria_id == categoria_id)
            .all()
        ]

    def buscar_por_ids(self, ids: list[int]) -> list[PontoTuristico]:
        if not ids:
            return []
        return self.sessao.query(PontoTuristico).filter(PontoTuristico.id.in_(ids)).all()

    def buscar_por_id(self, ponto_id: int) -> PontoTuristico | None:
        return self.sessao.query(PontoTuristico).filter(PontoTuristico.id == ponto_id).first()

    def buscar_ponto_categorias(self, ids_pontos: list[int]) -> list[PontoCategoria]:
        if not ids_pontos:
            return []
        return (
            self.sessao.query(PontoCategoria)
            .filter(PontoCategoria.ponto_id.in_(ids_pontos))
            .all()
        )


class RepositorioRota:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self) -> list[Rota]:
        return self.sessao.query(Rota).order_by(Rota.id).all()

    def buscar_rota_pontos(self, rota_id: int) -> list[RotaPonto]:
        return (
            self.sessao.query(RotaPonto)
            .filter(RotaPonto.rota_id == rota_id)
            .order_by(RotaPonto.ordem)
            .all()
        )

    def buscar_rota_pontos_por_ponto_ids(self, ids_pontos: list[int]) -> list[RotaPonto]:
        if not ids_pontos:
            return []
        return (
            self.sessao.query(RotaPonto)
            .filter(RotaPonto.ponto_id.in_(ids_pontos))
            .all()
        )
