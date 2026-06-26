from typing import Protocol


class ContratoClienteAutenticacao(Protocol):
    """ISP: interface mínima para consulta de usuários (serviço auth)."""

    def buscar_usuario_por_id(self, usuario_id: int) -> dict | None: ...

    def buscar_usuarios_em_lote(self, ids_usuarios: list[int]) -> dict[int, dict]: ...


class ContratoClienteConteudo(Protocol):
    """ISP: interface mínima para consulta de pontos turísticos (serviço content)."""

    def buscar_ponto_por_id(self, ponto_id: int) -> dict | None: ...

    def listar_pontos_turisticos(self, categoria_id: int | None = None) -> list[dict]: ...

    def buscar_pontos_por_ids(self, ids: list[int]) -> list[dict]: ...
