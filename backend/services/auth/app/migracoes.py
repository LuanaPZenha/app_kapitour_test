from datetime import date, datetime
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.infraestrutura.persistencia.modelos import UsuarioModelo
from kapitour_shared.banco_dados import motor_banco
from kapitour_shared.database.migracoes import executar_migracoes as executar_migracoes_base
from kapitour_shared.security.passwords import gerar_hash_senha

_ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def executar_migracoes() -> None:
    executar_migracoes_base(_ALEMBIC_INI)
    _migrar_colunas_legadas_sqlite()


def _migrar_colunas_legadas_sqlite() -> None:
    """Adiciona colunas em SQLite legados criados antes do Alembic."""
    if not str(motor_banco.url).startswith("sqlite"):
        return
    insp = inspect(motor_banco)
    if not insp.has_table("usuarios"):
        return
    colunas = {c["name"] for c in insp.get_columns("usuarios")}
    with motor_banco.begin() as conn:
        if "email_verificado" not in colunas:
            conn.execute(
                text("ALTER TABLE usuarios ADD COLUMN email_verificado BOOLEAN DEFAULT 0")
            )


def _montar_usuarios_demo() -> list[UsuarioModelo]:
    return [
        UsuarioModelo(
            auth_id="00000000-0000-0000-0000-000000000001",
            nome="Administrador",
            email="admin@kapitour.com",
            cpf="000.000.000-00",
            sexo="Masculino",
            data_nascimento=date(1990, 1, 1),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=1,
            senha_hash=gerar_hash_senha("admin123"),
            email_verificado=True,
        ),
        UsuarioModelo(
            auth_id="00000000-0000-0000-0000-000000000002",
            nome="Parceiro Demo",
            email="parceiro@kapitour.com",
            cpf="111.111.111-11",
            sexo="Feminino",
            data_nascimento=date(1988, 5, 10),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=2,
            senha_hash=gerar_hash_senha("parceiro123"),
            email_verificado=True,
        ),
        UsuarioModelo(
            auth_id="00000000-0000-0000-0000-000000000003",
            nome="Usuário Demo",
            email="user@kapitour.com",
            cpf="222.222.222-22",
            sexo="Masculino",
            data_nascimento=date(1995, 3, 15),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=3,
            senha_hash=gerar_hash_senha("user123"),
            email_verificado=True,
        ),
    ]


def semear_dados_iniciais(sessao: Session) -> None:
    emails_existentes = {email for (email,) in sessao.query(UsuarioModelo.email).all()}
    usuarios_demo = [u for u in _montar_usuarios_demo() if u.email not in emails_existentes]
    if usuarios_demo:
        sessao.add_all(usuarios_demo)
        sessao.commit()
