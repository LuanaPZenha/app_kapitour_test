from pathlib import Path

from sqlalchemy.orm import Session

from app.infraestrutura.persistencia.modelos import PontoTuristico
from kapitour_shared.database.migracoes import executar_migracoes as executar_migracoes_base

_ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def executar_migracoes() -> None:
    executar_migracoes_base(_ALEMBIC_INI)


def semear_dados_iniciais(sessao: Session) -> None:
    """Não insere dados de demo (Salvador).

    Os pontos e rotas de Maricá vêm de:
    - `database/kapitour.db` migrado via `backend/scripts/split_database.py`, ou
    - `backend/scripts/ensure_microservice_data.py` (automático no Docker quando kapitour.db existe).
    - `backend/scripts/update_pontos_marica.py` para atualizar o catálogo curado.
    """
    if sessao.query(PontoTuristico).count() > 0:
        return
