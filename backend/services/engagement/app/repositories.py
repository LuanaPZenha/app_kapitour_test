from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Avaliacao, Favorito, PontoAvaliacao


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
