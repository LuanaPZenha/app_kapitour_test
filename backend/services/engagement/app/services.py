from sqlalchemy.orm import Session

from app.repositories import FavoriteRepository
from kapitour_shared.clients import ContentClient


class FavoriteService:
    def __init__(self, db: Session):
        self.favorites = FavoriteRepository(db)
        self.content = ContentClient()

    def list_with_places(self, usuario_id: int) -> list[dict]:
        favoritos = self.favorites.list_by_user(usuario_id)
        ponto_ids = [fav.ponto_id for fav in favoritos]
        pontos_map = {p["id"]: p for p in self.content.get_pontos_by_ids(ponto_ids)}
        result = []
        for fav in favoritos:
            ponto = pontos_map.get(fav.ponto_id)
            ponto_data = None
            if ponto:
                ponto_data = {
                    "id": ponto["id"],
                    "nome": ponto["nome"],
                    "descricao": ponto.get("descricao"),
                    "latitude": ponto.get("latitude"),
                    "longitude": ponto.get("longitude"),
                    "url_img": ponto.get("url_img"),
                    "rua_numero": ponto.get("rua_numero"),
                }
            result.append(
                {
                    "id": fav.id,
                    "usuario_id": fav.usuario_id,
                    "ponto_id": fav.ponto_id,
                    "data_adicionado": fav.data_adicionado.isoformat(),
                    "pontos_turisticos": ponto_data,
                }
            )
        return result
