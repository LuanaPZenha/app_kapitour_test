from sqlalchemy.orm import Session

from app.repositories import UserRepository
from app.schemas import UsuarioResponse
from kapitour_shared.auth_tokens import create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, nome, email, password, **kwargs) -> dict:
        if self.users.email_exists(email):
            raise ValueError("Este email já está cadastrado.")
        user = self.users.create(
            nome=nome,
            email=email,
            password=password,
            cpf=kwargs.get("cpf"),
            sexo=kwargs.get("sexo"),
            data_nascimento=kwargs.get("data_nascimento"),
            tipo_usuario_id=kwargs.get("tipo_usuario_id", 3),
        )
        token = create_access_token(user.auth_id, user.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(user),
        }

    def login(self, email: str, password: str) -> dict:
        user = self.users.authenticate(email, password)
        if not user:
            raise ValueError("Credenciais inválidas.")
        token = create_access_token(user.auth_id, user.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(user),
        }


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def get_by_auth_id(self, auth_id: str):
        return self.users.get_by_auth_id(auth_id)

    def update(self, auth_id: str, data: dict):
        user = self.users.get_by_auth_id(auth_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        if data.get("email"):
            existing = self.users.get_by_email(data["email"])
            if existing and existing.id != user.id:
                raise ValueError("Email já cadastrado.")
        return self.users.update(user, data)
