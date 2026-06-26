from datetime import date, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Usuario
from kapitour_shared.auth_tokens import hash_password, verify_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_auth_id(self, auth_id: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.auth_id == auth_id).first()

    def get_by_id(self, user_id: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()

    def get_by_ids(self, user_ids: list[int]) -> list[Usuario]:
        if not user_ids:
            return []
        return self.db.query(Usuario).filter(Usuario.id.in_(user_ids)).all()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email.lower()).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, nome: str, email: str, password: str, **kwargs) -> Usuario:
        user = Usuario(
            auth_id=str(uuid4()),
            nome=nome,
            email=email.lower(),
            senha_hash=hash_password(password),
            data_criacao=datetime.utcnow(),
            **kwargs,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: Usuario, data: dict) -> Usuario:
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Usuario | None:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.senha_hash):
            return None
        return user
