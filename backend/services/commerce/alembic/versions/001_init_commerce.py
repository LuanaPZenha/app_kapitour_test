"""init commerce tables

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
        "tipos_produto",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "campanhas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("data_inicio", sa.Date(), nullable=True),
        sa.Column("data_fim", sa.Date(), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=True),
        sa.Column("criada_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("valor_unid", sa.Float(), nullable=True),
        sa.Column("tipo_id", sa.Integer(), nullable=True),
        sa.Column("imagem_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["tipo_id"], ["tipos_produto.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "estoque",
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("produto_id"),
    )
    op.create_table(
        "cupons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("criado_por", sa.Integer(), nullable=True),
        sa.Column("parceiro_id", sa.Integer(), nullable=True),
        sa.Column("data_validade", sa.Date(), nullable=True),
        sa.Column("data_criacao", sa.DateTime(), nullable=True),
        sa.Column("quantidade_disponivel", sa.Integer(), nullable=True),
        sa.Column("campanha_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["campanha_id"], ["campanhas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cupons_parceiro_id", "cupons", ["parceiro_id"])
    op.create_table(
        "cupons_resgatados",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cupom_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("data_resgate", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["cupom_id"], ["cupons.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cupom_id", "usuario_id"),
    )
    op.create_index("ix_cupons_resgatados_usuario_id", "cupons_resgatados", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_cupons_resgatados_usuario_id", table_name="cupons_resgatados")
    op.drop_table("cupons_resgatados")
    op.drop_index("ix_cupons_parceiro_id", table_name="cupons")
    op.drop_table("cupons")
    op.drop_table("estoque")
    op.drop_table("produtos")
    op.drop_table("campanhas")
    op.drop_table("tipos_produto")
