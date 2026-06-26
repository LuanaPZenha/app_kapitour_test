from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UsuarioResponse"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    cpf: str | None = None
    sexo: str | None = None
    data_nascimento: date | None = None
    password: str = Field(min_length=6)


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

    class Config:
        from_attributes = True


class UsuarioUpdateRequest(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    sexo: str | None = None
