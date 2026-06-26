import httpx

from kapitour_shared.configuracao import configuracoes


class ClienteAutenticacao:
    """Cliente HTTP para o serviço de autenticação (comunicação entre microserviços)."""

    def __init__(self, url_base: str | None = None):
        self._url_base = (url_base or configuracoes.auth_service_url).rstrip("/")
        self._cabecalhos = {"X-Internal-Key": configuracoes.internal_service_key}

    def buscar_usuario_por_id(self, usuario_id: int) -> dict | None:
        with httpx.Client(timeout=10.0) as cliente:
            resposta = cliente.get(
                f"{self._url_base}/api/internal/usuarios/{usuario_id}",
                headers=self._cabecalhos,
            )
            if resposta.status_code == 404:
                return None
            resposta.raise_for_status()
            return resposta.json()

    def buscar_usuarios_em_lote(self, ids_usuarios: list[int]) -> dict[int, dict]:
        if not ids_usuarios:
            return {}

        ids = ",".join(str(i) for i in sorted(set(ids_usuarios)))
        with httpx.Client(timeout=10.0) as cliente:
            resposta = cliente.get(
                f"{self._url_base}/api/internal/usuarios/batch",
                params={"ids": ids},
                headers=self._cabecalhos,
            )
            resposta.raise_for_status()
            itens = resposta.json()
            return {item["id"]: item for item in itens}


class ClienteConteudo:
    """Cliente HTTP para o serviço de conteúdo turístico."""

    def __init__(self, url_base: str | None = None):
        self._url_base = (url_base or configuracoes.content_service_url).rstrip("/")

    def buscar_ponto_por_id(self, ponto_id: int) -> dict | None:
        with httpx.Client(timeout=10.0) as cliente:
            resposta = cliente.get(f"{self._url_base}/api/pontos-turisticos/{ponto_id}")
            if resposta.status_code == 404:
                return None
            resposta.raise_for_status()
            return resposta.json()

    def listar_pontos_turisticos(self, categoria_id: int | None = None) -> list[dict]:
        parametros = {}
        if categoria_id is not None:
            parametros["categoria_id"] = categoria_id

        with httpx.Client(timeout=15.0) as cliente:
            resposta = cliente.get(
                f"{self._url_base}/api/pontos-turisticos",
                params=parametros,
            )
            resposta.raise_for_status()
            return resposta.json()

    def buscar_pontos_por_ids(self, ids: list[int]) -> list[dict]:
        if not ids:
            return []

        with httpx.Client(timeout=15.0) as cliente:
            resposta = cliente.get(
                f"{self._url_base}/api/internal/pontos/batch",
                params={"ids": ",".join(str(i) for i in ids)},
            )
            resposta.raise_for_status()
            return resposta.json()
