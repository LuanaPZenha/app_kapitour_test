from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class RespostaPaginada(BaseModel, Generic[T]):
    itens: list[T]
    pagina: int = Field(ge=1)
    tamanho: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_paginas: int = Field(ge=0)


def paginar(itens: list, pagina: int = 1, tamanho: int = 20) -> tuple[list, int]:
    pagina = max(1, pagina)
    tamanho = max(1, min(tamanho, 100))
    total = len(itens)
    inicio = (pagina - 1) * tamanho
    return itens[inicio : inicio + tamanho], total


def montar_resposta_paginada(itens: list, pagina: int, tamanho: int) -> dict:
    fatia, total = paginar(itens, pagina, tamanho)
    total_paginas = (total + tamanho - 1) // tamanho if tamanho else 0
    return {
        "itens": fatia,
        "pagina": max(1, pagina),
        "tamanho": max(1, min(tamanho, 100)),
        "total": total,
        "total_paginas": total_paginas,
    }
