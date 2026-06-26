from typing import Protocol, TypeVar

TEntidade = TypeVar("TEntidade")


class ContratoRepositorioLeitura(Protocol[TEntidade]):
    """ISP: operações de leitura genéricas."""

    def buscar_por_id(self, entidade_id: int) -> TEntidade | None: ...
