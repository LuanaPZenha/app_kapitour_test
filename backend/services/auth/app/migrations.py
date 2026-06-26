from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import Usuario
from kapitour_shared.auth_tokens import hash_password
from kapitour_shared.database import Base, engine


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)


def _build_demo_users() -> list[Usuario]:
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
            senha_hash=hash_password("admin123"),
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
            senha_hash=hash_password("parceiro123"),
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
            senha_hash=hash_password("user123"),
        ),
    ]


def seed_initial_data(db: Session) -> None:
    existing_emails = {email for (email,) in db.query(Usuario.email).all()}
    demo_users = [user for user in _build_demo_users() if user.email not in existing_emails]
    if demo_users:
        db.add_all(demo_users)
        db.commit()
