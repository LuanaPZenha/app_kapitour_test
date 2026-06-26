from datetime import datetime

from pydantic import BaseModel


class CheckinRequest(BaseModel):
    ponto_turistico_id: int
    latitude: float | None = None
    longitude: float | None = None


class EcoRegistrarRequest(BaseModel):
    eco_atividade_id: int


class DiarioCreate(BaseModel):
    ponto_turistico_id: int | None = None
    checkin_id: int | None = None
    comentario: str | None = None
    foto: str | None = None
