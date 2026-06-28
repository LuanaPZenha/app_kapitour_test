from datetime import date, datetime

from pydantic import BaseModel, Field


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None = None
    valor_unid: float | None = None
    tipo_id: int | None = None
    imagem_url: str | None = None

    class Config:
        from_attributes = True


class ProdutosPaginadosResponse(BaseModel):
    itens: list[ProdutoResponse]
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_paginas: int = Field(ge=0)


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


class CupomResgateRequest(BaseModel):
    cupom_id: int
    usuario_id: int | None = None
    parceiro_id: int | None = None
