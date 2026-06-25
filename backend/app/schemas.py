from datetime import date, datetime
from typing import Any

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


class CategoriaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class PontoTuristicoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    url_img: str | None = None
    rua_numero: str | None = None

    class Config:
        from_attributes = True


class RotaResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None = None

    class Config:
        from_attributes = True


class RotaPontoResponse(BaseModel):
    id: int
    rota_id: int
    ponto_id: int
    ordem: int

    class Config:
        from_attributes = True


class FavoritoCreate(BaseModel):
    usuario_id: int
    ponto_id: int


class FavoritoResponse(BaseModel):
    id: int
    usuario_id: int
    ponto_id: int
    data_adicionado: datetime
    pontos_turisticos: PontoTuristicoResponse | None = None

    class Config:
        from_attributes = True


class AvaliacaoCreate(BaseModel):
    usuario_id: int
    ponto_id: int
    nota: int
    comentario: str | None = None


class AvaliacaoUpdate(BaseModel):
    nota: int
    comentario: str | None = None


class AvaliacaoResponse(BaseModel):
    id: int
    usuario_id: int
    ponto_id: int
    nota: int
    comentario: str | None = None
    data_avaliacao: datetime

    class Config:
        from_attributes = True


class PontoAvaliacaoCreate(BaseModel):
    ponto_id: int
    usuario_id: int | None = None
    nota: int
    comentario: str | None = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    valor_unid: float | None = None
    tipo_id: int | None = None
    imagem_url: str | None = None

    class Config:
        from_attributes = True


class TipoProdutoResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class EstoqueResponse(BaseModel):
    produto_id: int
    quantidade: int

    class Config:
        from_attributes = True


class CampanhaResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    ativa: bool
    criada_em: datetime | None = None

    class Config:
        from_attributes = True


class CupomResponse(BaseModel):
    id: int
    codigo: str
    descricao: str | None = None
    criado_por: int | None = None
    parceiro_id: int | None = None
    data_validade: date | None = None
    data_criacao: datetime | None = None
    quantidade_disponivel: int
    campanha_id: int | None = None
    campanha: CampanhaResponse | None = None

    class Config:
        from_attributes = True


class CupomResgateRequest(BaseModel):
    cupom_id: int
    usuario_id: int
    parceiro_id: int | None = None


class MessageResponse(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
    data: Any | None = None


# ─────────────────────────────────────────────────────────────
# KapiPass — Passaporte Turístico Gamificado
# ─────────────────────────────────────────────────────────────


class NivelResponse(BaseModel):
    id: int
    nome: str
    xp_minimo: int
    ordem: int

    class Config:
        from_attributes = True


class CheckinRequest(BaseModel):
    ponto_turistico_id: int
    latitude: float | None = None
    longitude: float | None = None


class CheckinResponse(BaseModel):
    id: int
    usuario_id: int
    ponto_turistico_id: int
    data_checkin: datetime
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True


class EcoRegistrarRequest(BaseModel):
    eco_atividade_id: int


class DiarioCreate(BaseModel):
    ponto_turistico_id: int | None = None
    checkin_id: int | None = None
    comentario: str | None = None
    foto: str | None = None
