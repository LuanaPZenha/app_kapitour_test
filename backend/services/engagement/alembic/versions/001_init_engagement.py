"""init engagement tables

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
        "favoritos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("ponto_id", sa.Integer(), nullable=False),
        sa.Column("data_adicionado", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "ponto_id"),
    )
    op.create_index("ix_favoritos_usuario_id", "favoritos", ["usuario_id"])
    op.create_index("ix_favoritos_ponto_id", "favoritos", ["ponto_id"])

    op.create_table(
        "avaliacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("ponto_id", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("data_avaliacao", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "ponto_id"),
    )
    op.create_index("ix_avaliacoes_usuario_id", "avaliacoes", ["usuario_id"])
    op.create_index("ix_avaliacoes_ponto_id", "avaliacoes", ["ponto_id"])

    op.create_table(
        "ponto_avaliacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ponto_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("data", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ponto_avaliacoes_ponto_id", "ponto_avaliacoes", ["ponto_id"])
    op.create_index("ix_ponto_avaliacoes_usuario_id", "ponto_avaliacoes", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_ponto_avaliacoes_usuario_id", table_name="ponto_avaliacoes")
    op.drop_index("ix_ponto_avaliacoes_ponto_id", table_name="ponto_avaliacoes")
    op.drop_table("ponto_avaliacoes")
    op.drop_index("ix_avaliacoes_ponto_id", table_name="avaliacoes")
    op.drop_index("ix_avaliacoes_usuario_id", table_name="avaliacoes")
    op.drop_table("avaliacoes")
    op.drop_index("ix_favoritos_ponto_id", table_name="favoritos")
    op.drop_index("ix_favoritos_usuario_id", table_name="favoritos")
    op.drop_table("favoritos")
