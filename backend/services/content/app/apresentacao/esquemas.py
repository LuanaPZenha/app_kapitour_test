from pydantic import BaseModel, ConfigDict, Field


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 1, "nome": "Praias"}]},
    )

    id: int
    nome: str


class PontoTuristicoResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nome": "Praia de Itaipuaçu",
                    "descricao": "Praia extensa em Maricá",
                    "latitude": -22.918,
                    "longitude": -42.818,
                    "url_img": None,
                    "rua_numero": "Av. Beira Mar",
                }
            ]
        },
    )

    id: int
    nome: str
    descricao: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    url_img: str | None = None
    rua_numero: str | None = None


class RotaResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 1, "nome": "Rota das Praias", "descricao": None}]},
    )

    id: int
    nome: str
    descricao: str | None = None


class PontosPaginadosResponse(BaseModel):
    itens: list[PontoTuristicoResponse]
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_paginas: int = Field(ge=0)


class RotasPaginadasResponse(BaseModel):
    itens: list[RotaResponse]
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_paginas: int = Field(ge=0)


class RotaPontoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rota_id: int
    ponto_id: int
    ordem: int
