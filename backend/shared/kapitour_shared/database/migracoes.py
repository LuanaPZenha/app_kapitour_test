"""Executa migrações Alembic ou create_all conforme configuração."""

from pathlib import Path

from alembic import command
from alembic.config import Config

from kapitour_shared.banco_dados import BaseModelo, motor_banco
from kapitour_shared.configuracao import configuracoes


def executar_migracoes_sqlalchemy() -> None:
    """Fallback — create_all para SQLite/desenvolvimento."""
    BaseModelo.metadata.create_all(bind=motor_banco)


def executar_migracoes_alembic(ini_path: Path) -> None:
    """Aplica migrações versionadas via Alembic."""
    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", configuracoes.database_url)
    command.upgrade(cfg, "head")


def executar_migracoes(ini_path: Path | None = None) -> None:
    if configuracoes.usar_alembic and ini_path and ini_path.exists():
        executar_migracoes_alembic(ini_path)
    else:
        executar_migracoes_sqlalchemy()
