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


# ─────────────────────────────────────────────────────────────
# KapiPass — Passaporte Turístico Gamificado
# ─────────────────────────────────────────────────────────────


class KapiPassNivel(Base):
    __tablename__ = "kapipass_niveis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    xp_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class UsuarioXp(Base):
    __tablename__ = "usuario_xp"

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nivel_atual: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class KapiPassCarimbo(Base):
    __tablename__ = "kapipass_carimbos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ponto_turistico_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    imagem: Mapped[str | None] = mapped_column(Text)
    raridade: Mapped[str] = mapped_column(String(50), default="comum")
    xp_recompensa: Mapped[int] = mapped_column(Integer, default=50)


class UsuarioCarimbo(Base):
    __tablename__ = "usuario_carimbos"
    __table_args__ = (UniqueConstraint("usuario_id", "carimbo_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    carimbo_id: Mapped[int] = mapped_column(ForeignKey("kapipass_carimbos.id"), nullable=False)
    data_obtencao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Checkin(Base):
    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ponto_turistico_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)
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
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    conquista_id: Mapped[int] = mapped_column(ForeignKey("conquistas.id"), nullable=False)
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
    colecao_id: Mapped[int] = mapped_column(ForeignKey("colecoes.id"), nullable=False)
    ponto_turistico_id: Mapped[int] = mapped_column(ForeignKey("pontos_turisticos.id"), nullable=False)


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
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    missao_id: Mapped[int] = mapped_column(ForeignKey("missoes.id"), nullable=False)
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
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    eco_atividade_id: Mapped[int] = mapped_column(ForeignKey("eco_atividades.id"), nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    pontuacao: Mapped[int] = mapped_column(Integer, default=0)


class DiarioViagem(Base):
    __tablename__ = "diario_viagem"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    ponto_turistico_id: Mapped[int | None] = mapped_column(ForeignKey("pontos_turisticos.id"))
    checkin_id: Mapped[int | None] = mapped_column(ForeignKey("checkins.id"))
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
    ponto_turistico_id: Mapped[int | None] = mapped_column(ForeignKey("pontos_turisticos.id"))
    carimbo_id: Mapped[int | None] = mapped_column(ForeignKey("kapipass_carimbos.id"))
    conquista_id: Mapped[int | None] = mapped_column(ForeignKey("conquistas.id"))
    xp_bonus: Mapped[int] = mapped_column(Integer, default=0)


class UsuarioTesouro(Base):
    __tablename__ = "usuario_tesouros"
    __table_args__ = (UniqueConstraint("usuario_id", "tesouro_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    tesouro_id: Mapped[int] = mapped_column(ForeignKey("tesouros.id"), nullable=False)
    data_conclusao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
