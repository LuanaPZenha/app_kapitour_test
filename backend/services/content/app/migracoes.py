from sqlalchemy.orm import Session

from app.infraestrutura.persistencia.modelos import PontoTuristico
from kapitour_shared.banco_dados import BaseModelo, motor_banco


def executar_migracoes() -> None:
    BaseModelo.metadata.create_all(bind=motor_banco)


def semear_dados_iniciais(sessao: Session) -> None:
    """Não insere dados de demo (Salvador).

    Os pontos e rotas de Maricá vêm de:
    - `database/kapitour.db` migrado via `backend/scripts/split_database.py`, ou
    - `backend/scripts/ensure_microservice_data.py` (automático no Docker quando kapitour.db existe).
    - `backend/scripts/update_pontos_marica.py` para atualizar o catálogo curado.
    """
    if sessao.query(PontoTuristico).count() > 0:
        return
