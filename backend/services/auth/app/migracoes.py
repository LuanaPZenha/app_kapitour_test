from datetime import date, datetime

from sqlalchemy.orm import Session

from app.modelos import Usuario
from kapitour_shared.autenticacao import gerar_hash_senha
from kapitour_shared.banco_dados import BaseModelo, motor_banco


def executar_migracoes() -> None:
    BaseModelo.metadata.create_all(bind=motor_banco)


def _montar_usuarios_demo() -> list[Usuario]:
    return [
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000001",
            nome="Administrador",
            email="admin@kapitour.com",
            cpf="000.000.000-00",
            sexo="Masculino",
            data_nascimento=date(1990, 1, 1),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=1,
            senha_hash=gerar_hash_senha("admin123"),
        ),
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000002",
            nome="Parceiro Demo",
            email="parceiro@kapitour.com",
            cpf="111.111.111-11",
            sexo="Feminino",
            data_nascimento=date(1988, 5, 10),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=2,
            senha_hash=gerar_hash_senha("parceiro123"),
        ),
        Usuario(
            auth_id="00000000-0000-0000-0000-000000000003",
            nome="Usuário Demo",
            email="user@kapitour.com",
            cpf="222.222.222-22",
            sexo="Masculino",
            data_nascimento=date(1995, 3, 15),
            data_criacao=datetime.utcnow(),
            tipo_usuario_id=3,
            senha_hash=gerar_hash_senha("user123"),
        ),
    ]


def semear_dados_iniciais(sessao: Session) -> None:
    emails_existentes = {email for (email,) in sessao.query(Usuario.email).all()}
    usuarios_demo = [u for u in _montar_usuarios_demo() if u.email not in emails_existentes]
    if usuarios_demo:
        sessao.add_all(usuarios_demo)
        sessao.commit()
