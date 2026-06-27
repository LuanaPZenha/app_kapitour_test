"""init kapipass tables

Revision ID: 001
Revises:
Create Date: 2026-06-27
"""

from typing import Sequence, Union

from alembic import op

from kapitour_shared.banco_dados import BaseModelo

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import app.infraestrutura.persistencia.modelos  # noqa: F401

    bind = op.get_bind()
    BaseModelo.metadata.create_all(bind)


def downgrade() -> None:
    bind = op.get_bind()
    BaseModelo.metadata.drop_all(bind)
