from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kapitour_shared.database import Base


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = (UniqueConstraint("usuario_id", "ponto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ponto_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    data_adicionado: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (UniqueConstraint("usuario_id", "ponto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ponto_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PontoAvaliacao(Base):
    __tablename__ = "ponto_avaliacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, index=True)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
