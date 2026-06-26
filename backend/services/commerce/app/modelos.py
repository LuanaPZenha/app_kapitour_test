from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kapitour_shared.banco_dados import BaseModelo


class TipoProduto(BaseModelo):
    __tablename__ = "tipos_produto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)


class Produto(BaseModelo):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    valor_unid: Mapped[float | None] = mapped_column(Float)
    tipo_id: Mapped[int | None] = mapped_column(ForeignKey("tipos_produto.id"))
    imagem_url: Mapped[str | None] = mapped_column(Text)


class Estoque(BaseModelo):
    __tablename__ = "estoque"

    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), primary_key=True)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)


class Campanha(BaseModelo):
    __tablename__ = "campanhas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Cupom(BaseModelo):
    __tablename__ = "cupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_por: Mapped[int | None] = mapped_column(Integer)
    parceiro_id: Mapped[int | None] = mapped_column(Integer, index=True)
    data_validade: Mapped[date | None] = mapped_column(Date)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer, default=0)
    campanha_id: Mapped[int | None] = mapped_column(ForeignKey("campanhas.id"))


class CupomResgatado(BaseModelo):
    __tablename__ = "cupons_resgatados"
    __table_args__ = (UniqueConstraint("cupom_id", "usuario_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cupom_id: Mapped[int] = mapped_column(ForeignKey("cupons.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    data_resgate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
