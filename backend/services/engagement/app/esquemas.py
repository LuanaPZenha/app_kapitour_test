from datetime import datetime

from pydantic import BaseModel


class FavoritoCreate(BaseModel):
    usuario_id: int
    ponto_id: int


class FavoritoResponse(BaseModel):
    id: int
    usuario_id: int
    ponto_id: int
    data_adicionado: datetime

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
