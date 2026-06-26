from sqlalchemy.orm import Session

from app.models import PontoTuristico
from kapitour_shared.database import Base, engine


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


def seed_initial_data(db: Session) -> None:
    """Não insere dados de demo (Salvador).

    Os pontos e rotas de Maricá vêm de:
    - `database/kapitour.db` migrado via `backend/scripts/split_database.py`, ou
    - `backend/scripts/ensure_microservice_data.py` (automático no Docker quando kapitour.db existe).
    - `backend/scripts/update_pontos_marica.py` para atualizar o catálogo curado.
    """
    if db.query(PontoTuristico).count() > 0:
        return
