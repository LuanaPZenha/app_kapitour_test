from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from kapitour_shared.configuracao import configuracoes


def _resolver_caminho_sqlite(url: str) -> str:
    if not url.startswith("sqlite:///"):
        return url
    relativo = url.replace("sqlite:///", "", 1)
    if relativo.startswith("/") or relativo.startswith(":"):
        return url
    caminho = Path(relativo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{caminho.as_posix()}"


def _criar_motor(url: str):
    url = _resolver_caminho_sqlite(url)
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=configuracoes.db_pool_size,
        max_overflow=configuracoes.db_max_overflow,
        pool_pre_ping=True,
    )


URL_BANCO = _resolver_caminho_sqlite(configuracoes.database_url)
motor_banco = _criar_motor(configuracoes.database_url)
FabricaSessao = sessionmaker(autocommit=False, autoflush=False, bind=motor_banco)


class BaseModelo(DeclarativeBase):
    pass


def obter_sessao_banco():
    sessao = FabricaSessao()
    try:
        yield sessao
    finally:
        sessao.close()
