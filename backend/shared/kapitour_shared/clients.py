import httpx

from kapitour_shared.config import settings


class AuthClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.auth_service_url).rstrip("/")
        self.headers = {"X-Internal-Key": settings.internal_service_key}

    def get_user(self, user_id: int) -> dict | None:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{self.base_url}/api/internal/usuarios/{user_id}",
                headers=self.headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    def batch_users(self, user_ids: list[int]) -> dict[int, dict]:
        if not user_ids:
            return {}
        ids = ",".join(str(i) for i in sorted(set(user_ids)))
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{self.base_url}/api/internal/usuarios/batch",
                params={"ids": ids},
                headers=self.headers,
            )
            response.raise_for_status()
            items = response.json()
            return {item["id"]: item for item in items}


class ContentClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.content_service_url).rstrip("/")

    def get_ponto(self, ponto_id: int) -> dict | None:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{self.base_url}/api/pontos-turisticos/{ponto_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    def list_pontos(self, categoria_id: int | None = None) -> list[dict]:
        params = {}
        if categoria_id is not None:
            params["categoria_id"] = categoria_id
        with httpx.Client(timeout=15.0) as client:
            response = client.get(f"{self.base_url}/api/pontos-turisticos", params=params)
            response.raise_for_status()
            return response.json()

    def get_pontos_by_ids(self, ids: list[int]) -> list[dict]:
        if not ids:
            return []
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{self.base_url}/api/internal/pontos/batch",
                params={"ids": ",".join(str(i) for i in ids)},
            )
            response.raise_for_status()
            return response.json()
