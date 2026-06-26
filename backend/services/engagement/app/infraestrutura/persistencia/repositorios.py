from datetime import datetime

from sqlalchemy.orm import Session

from app.infraestrutura.persistencia.modelos import Avaliacao, Favorito, PontoAvaliacao


class RepositorioFavorito:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_por_usuario(self, usuario_id: int) -> list[Favorito]:
        return self.sessao.query(Favorito).filter(Favorito.usuario_id == usuario_id).all()

    def buscar(self, usuario_id: int, ponto_id: int) -> Favorito | None:
        return (
            self.sessao.query(Favorito)
            .filter(Favorito.usuario_id == usuario_id, Favorito.ponto_id == ponto_id)
            .first()
        )

    def criar(self, usuario_id: int, ponto_id: int) -> Favorito:
        favorito = Favorito(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            data_adicionado=datetime.utcnow(),
        )
        self.sessao.add(favorito)
        self.sessao.commit()
        self.sessao.refresh(favorito)
        return favorito

    def excluir(self, usuario_id: int, ponto_id: int) -> bool:
        favorito = self.buscar(usuario_id, ponto_id)
        if not favorito:
            return False
        self.sessao.delete(favorito)
        self.sessao.commit()
        return True


class RepositorioAvaliacao:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_por_ponto(self, ponto_id: int) -> list[Avaliacao]:
        return self.sessao.query(Avaliacao).filter(Avaliacao.ponto_id == ponto_id).all()

    def buscar_avaliacao_usuario(self, usuario_id: int, ponto_id: int) -> Avaliacao | None:
        return (
            self.sessao.query(Avaliacao)
            .filter(Avaliacao.usuario_id == usuario_id, Avaliacao.ponto_id == ponto_id)
            .first()
        )

    def criar(self, usuario_id: int, ponto_id: int, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao = Avaliacao(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            nota=nota,
            comentario=comentario,
            data_avaliacao=datetime.utcnow(),
        )
        self.sessao.add(avaliacao)
        self.sessao.commit()
        self.sessao.refresh(avaliacao)
        return avaliacao

    def atualizar(self, avaliacao: Avaliacao, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao.nota = nota
        avaliacao.comentario = comentario
        avaliacao.data_avaliacao = datetime.utcnow()
        self.sessao.commit()
        self.sessao.refresh(avaliacao)
        return avaliacao

    def criar_ponto_avaliacao(
        self, ponto_id: int, usuario_id: int | None, nota: int, comentario: str | None
    ) -> PontoAvaliacao:
        item = PontoAvaliacao(
            ponto_id=ponto_id,
            usuario_id=usuario_id,
            nota=nota,
            comentario=comentario,
            data=datetime.utcnow(),
        )
        self.sessao.add(item)
        self.sessao.commit()
        self.sessao.refresh(item)
        return item

    def listar_ponto_avaliacoes(self, ponto_id: int) -> list[PontoAvaliacao]:
        return self.sessao.query(PontoAvaliacao).filter(PontoAvaliacao.ponto_id == ponto_id).all()

    def buscar_por_id(self, avaliacao_id: int) -> Avaliacao | None:
        return self.sessao.query(Avaliacao).filter(Avaliacao.id == avaliacao_id).first()
