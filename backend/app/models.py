from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    cpf: Mapped[str | None] = mapped_column(String(20))
    sexo: Mapped[str | None] = mapped_column(String(20))
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tipo_usuario_id: Mapped[int] = mapped_column(Integer, default=3)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)


class PontoTuristico(Base):
    __tablename__ = "pontos_turisticos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    url_img: Mapped[str | None] = mapped_column(Text)
    rua_numero: Mapped[str | None] = mapped_column(String(255))


class PontoCategoria(Base):
    __tablename__ = "ponto_categoria"
    __table_args__ = (UniqueConstraint("ponto_id", "categoria_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)


class Rota(Base):
    __tablename__ = "rotas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)


class RotaPonto(Base):
    __tablename__ = "rota_ponto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rota_id: Mapped[int] = mapped_column(ForeignKey("rotas.id"), nullable=False)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0)


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = (UniqueConstraint("usuario_id", "ponto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    data_adicionado: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (UniqueConstraint("usuario_id", "ponto_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PontoAvaliacao(Base):
    __tablename__ = "ponto_avaliacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TipoProduto(Base):
    __tablename__ = "tipos_produto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    valor_unid: Mapped[float | None] = mapped_column(Float)
    tipo_id: Mapped[int | None] = mapped_column(ForeignKey("tipos_produto.id"))
    imagem_url: Mapped[str | None] = mapped_column(Text)


class Estoque(Base):
    __tablename__ = "estoque"

    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), primary_key=True)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)


class Campanha(Base):
    __tablename__ = "campanhas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Cupom(Base):
    __tablename__ = "cupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    parceiro_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    data_validade: Mapped[date | None] = mapped_column(Date)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer, default=0)
    campanha_id: Mapped[int | None] = mapped_column(ForeignKey("campanhas.id"))


class CupomResgatado(Base):
    __tablename__ = "cupons_resgatados"
    __table_args__ = (UniqueConstraint("cupom_id", "usuario_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cupom_id: Mapped[int] = mapped_column(ForeignKey("cupons.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    data_resgate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
