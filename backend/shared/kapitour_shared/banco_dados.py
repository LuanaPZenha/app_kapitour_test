from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

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


URL_BANCO = _resolver_caminho_sqlite(configuracoes.database_url)
argumentos_conexao = (
    {"check_same_thread": False} if URL_BANCO.startswith("sqlite") else {}
)

motor_banco = create_engine(URL_BANCO, connect_args=argumentos_conexao)
FabricaSessao = sessionmaker(autocommit=False, autoflush=False, bind=motor_banco)


class BaseModelo(DeclarativeBase):
    pass


def obter_sessao_banco():
    sessao = FabricaSessao()
    try:
        yield sessao
    finally:
        sessao.close()
