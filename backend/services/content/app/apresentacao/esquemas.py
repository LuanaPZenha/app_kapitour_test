from pydantic import BaseModel


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
