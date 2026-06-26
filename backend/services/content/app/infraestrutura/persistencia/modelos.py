from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kapitour_shared.banco_dados import BaseModelo


class Categoria(BaseModelo):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)


class PontoTuristico(BaseModelo):
    __tablename__ = "pontos_turisticos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    url_img: Mapped[str | None] = mapped_column(Text)
    rua_numero: Mapped[str | None] = mapped_column(String(255))


class PontoCategoria(BaseModelo):
    __tablename__ = "ponto_categoria"
    __table_args__ = (UniqueConstraint("ponto_id", "categoria_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)


class Rota(BaseModelo):
    __tablename__ = "rotas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)


class RotaPonto(BaseModelo):
    __tablename__ = "rota_ponto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rota_id: Mapped[int] = mapped_column(ForeignKey("rotas.id"), nullable=False)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
