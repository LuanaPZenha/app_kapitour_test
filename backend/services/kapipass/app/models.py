from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from kapitour_shared.database import Base


class KapiPassNivel(Base):
    __tablename__ = "kapipass_niveis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    xp_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class UsuarioXp(Base):
    __tablename__ = "usuario_xp"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nivel_atual: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KapiPassCarimbo(Base):
    __tablename__ = "kapipass_carimbos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_turistico_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    imagem: Mapped[str | None] = mapped_column(Text)
    raridade: Mapped[str] = mapped_column(String(50), default="comum")
    xp_recompensa: Mapped[int] = mapped_column(Integer, default=50)


class UsuarioCarimbo(Base):
    __tablename__ = "usuario_carimbos"
    __table_args__ = (UniqueConstraint("usuario_id", "carimbo_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    carimbo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_obtencao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Checkin(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ponto_turistico_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    data_checkin: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)


class Conquista(Base):
    __tablename__ = "conquistas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    icone: Mapped[str | None] = mapped_column(String(100))
    xp_bonus: Mapped[int] = mapped_column(Integer, default=0)


class UsuarioConquista(Base):
    __tablename__ = "usuario_conquistas"
    __table_args__ = (UniqueConstraint("usuario_id", "conquista_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    conquista_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_desbloqueio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Colecao(Base):
    __tablename__ = "colecoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    imagem: Mapped[str | None] = mapped_column(Text)


class ColecaoPonto(Base):
    __tablename__ = "colecao_pontos"
    __table_args__ = (UniqueConstraint("colecao_id", "ponto_turistico_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    colecao_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ponto_turistico_id: Mapped[int] = mapped_column(Integer, nullable=False)


class Missao(Base):
    __tablename__ = "missoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(50), default="explorar")
    objetivo_quantidade: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    recompensa: Mapped[str | None] = mapped_column(String(255))
    dias_validade: Mapped[int | None] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class UsuarioMissao(Base):
    __tablename__ = "usuario_missoes"
    __table_args__ = (UniqueConstraint("usuario_id", "missao_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    missao_id: Mapped[int] = mapped_column(Integer, nullable=False)
    progresso: Mapped[int] = mapped_column(Integer, default=0)
    concluida: Mapped[bool] = mapped_column(Boolean, default=False)
    data_inicio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_conclusao: Mapped[datetime | None] = mapped_column(DateTime)


class EcoAtividade(Base):
    __tablename__ = "eco_atividades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(50), default="trilha")
    pontuacao_eco: Mapped[int] = mapped_column(Integer, default=0)
    xp_recompensa: Mapped[int] = mapped_column(Integer, default=0)


class UsuarioEcoAtividade(Base):
    __tablename__ = "usuario_eco_atividades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    eco_atividade_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    pontuacao: Mapped[int] = mapped_column(Integer, default=0)


class DiarioViagem(Base):
    __tablename__ = "diario_viagem"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ponto_turistico_id: Mapped[int | None] = mapped_column(Integer)
    checkin_id: Mapped[int | None] = mapped_column(Integer)
    comentario: Mapped[str | None] = mapped_column(Text)
    foto: Mapped[str | None] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Tesouro(Base):
    __tablename__ = "tesouros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    pista: Mapped[str | None] = mapped_column(Text)
    enigma: Mapped[str | None] = mapped_column(Text)
    ponto_turistico_id: Mapped[int | None] = mapped_column(Integer)
    carimbo_id: Mapped[int | None] = mapped_column(Integer)
    conquista_id: Mapped[int | None] = mapped_column(Integer)
    xp_bonus: Mapped[int] = mapped_column(Integer, default=0)


class UsuarioTesouro(Base):
    __tablename__ = "usuario_tesouros"
    __table_args__ = (UniqueConstraint("usuario_id", "tesouro_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tesouro_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_conclusao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
