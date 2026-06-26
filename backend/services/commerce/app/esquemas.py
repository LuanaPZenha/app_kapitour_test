from datetime import date, datetime

from pydantic import BaseModel


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


class CupomResgateRequest(BaseModel):
    cupom_id: int
    usuario_id: int
    parceiro_id: int | None = None
