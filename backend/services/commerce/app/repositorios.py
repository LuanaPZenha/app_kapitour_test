from datetime import datetime

from sqlalchemy.orm import Session

from app.modelos import Campanha, Cupom, CupomResgatado, Estoque, Produto, TipoProduto


class RepositorioLoja:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_produtos(self) -> list[Produto]:
        return self.sessao.query(Produto).all()

    def listar_tipos(self) -> list[TipoProduto]:
        return self.sessao.query(TipoProduto).all()

    def listar_estoque(self) -> list[Estoque]:
        return self.sessao.query(Estoque).all()


class RepositorioCupom:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_disponiveis(self, parceiro_id: int | None = None) -> list[Cupom]:
        consulta = self.sessao.query(Cupom).filter(Cupom.quantidade_disponivel > 0)
        if parceiro_id:
            consulta = consulta.filter(Cupom.parceiro_id == parceiro_id)
        return consulta.all()

    def buscar_por_id(self, cupom_id: int) -> Cupom | None:
        return self.sessao.query(Cupom).filter(Cupom.id == cupom_id).first()

    def buscar_campanha(self, campanha_id: int) -> Campanha | None:
        return self.sessao.query(Campanha).filter(Campanha.id == campanha_id).first()

    def listar_resgatados(self, usuario_id: int) -> list[CupomResgatado]:
        return (
            self.sessao.query(CupomResgatado)
            .filter(CupomResgatado.usuario_id == usuario_id)
            .all()
        )

    def ja_resgatado(self, cupom_id: int, usuario_id: int) -> bool:
        return (
            self.sessao.query(CupomResgatado)
            .filter(
                CupomResgatado.cupom_id == cupom_id,
                CupomResgatado.usuario_id == usuario_id,
            )
            .first()
            is not None
        )

    def resgatar(self, cupom: Cupom, usuario_id: int) -> CupomResgatado:
        resgate = CupomResgatado(
            cupom_id=cupom.id,
            usuario_id=usuario_id,
            data_resgate=datetime.utcnow(),
        )
        cupom.quantidade_disponivel -= 1
        self.sessao.add(resgate)
        self.sessao.commit()
        self.sessao.refresh(resgate)
        return resgate

    def listar_por_parceiro(self, parceiro_id: int) -> list[Cupom]:
        return self.sessao.query(Cupom).filter(Cupom.parceiro_id == parceiro_id).all()
