from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from kapitour_shared.security.rbac import Role, role_de_tipo_usuario


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    user: "UsuarioResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["turista@email.com"])
    password: str = Field(min_length=1, examples=["SenhaForte1"])


class RegisterRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    cpf: str | None = Field(default=None, max_length=20)
    sexo: str | None = Field(default=None, max_length=20)
    data_nascimento: date | None = None
    password: str = Field(min_length=6)


class ChangePasswordRequest(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8)


class UsuarioResponse(BaseModel):
    id: int
    auth_id: str
    nome: str
    email: str
    cpf: str | None = None
    sexo: str | None = None
    data_nascimento: date | None = None
    data_criacao: datetime | None = None
    tipo_usuario_id: int
    email_verificado: bool = False
    role: str | None = None

    class Config:
        from_attributes = True


class UsuarioUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    cpf: str | None = Field(default=None, max_length=20)
    sexo: str | None = Field(default=None, max_length=20)


def role_para_resposta(tipo_usuario_id: int) -> str:
    return role_de_tipo_usuario(tipo_usuario_id).value
