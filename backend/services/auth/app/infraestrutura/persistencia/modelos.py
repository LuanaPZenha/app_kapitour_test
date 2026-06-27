from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from kapitour_shared.banco_dados import BaseModelo


class UsuarioModelo(BaseModelo):
    """Modelo ORM — camada de infraestrutura."""

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
    email_verificado: Mapped[bool] = mapped_column(Boolean, default=False)


class TokenOperacaoModelo(BaseModelo):
    """Tokens de recuperação de senha e confirmação de e-mail."""

    __tablename__ = "tokens_operacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    auth_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(32), nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
