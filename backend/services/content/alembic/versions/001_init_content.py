"""init content tables

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
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pontos_turisticos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("url_img", sa.Text(), nullable=True),
        sa.Column("rua_numero", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ponto_categoria",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ponto_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["ponto_id"], ["pontos_turisticos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ponto_id", "categoria_id"),
    )
    op.create_table(
        "rotas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rota_ponto",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rota_id", sa.Integer(), nullable=False),
        sa.Column("ponto_id", sa.Integer(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["ponto_id"], ["pontos_turisticos.id"]),
        sa.ForeignKeyConstraint(["rota_id"], ["rotas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("rota_ponto")
    op.drop_table("rotas")
    op.drop_table("ponto_categoria")
    op.drop_table("pontos_turisticos")
    op.drop_table("categorias")
