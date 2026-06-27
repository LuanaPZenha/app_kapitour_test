"""init auth tables

Revision ID: 001
Revises:
Create Date: 2026-06-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("auth_id", sa.String(length=36), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("cpf", sa.String(length=20), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("data_criacao", sa.DateTime(), nullable=True),
        sa.Column("tipo_usuario_id", sa.Integer(), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_auth_id", "usuarios", ["auth_id"], unique=True)
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "tokens_operacao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("auth_id", sa.String(length=36), nullable=False),
        sa.Column("tipo", sa.String(length=32), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("usado", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tokens_operacao_token", "tokens_operacao", ["token"], unique=True)
    op.create_index("ix_tokens_operacao_auth_id", "tokens_operacao", ["auth_id"])


def downgrade() -> None:
    op.drop_index("ix_tokens_operacao_auth_id", table_name="tokens_operacao")
    op.drop_index("ix_tokens_operacao_token", table_name="tokens_operacao")
    op.drop_table("tokens_operacao")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_auth_id", table_name="usuarios")
    op.drop_table("usuarios")
