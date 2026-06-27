from pathlib import Path

from kapitour_shared.database.migracoes import executar_migracoes as executar_migracoes_base

_ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def executar_migracoes() -> None:
    executar_migracoes_base(_ALEMBIC_INI)
