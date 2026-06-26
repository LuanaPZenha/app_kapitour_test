from app.repositorios import RepositorioFavorito
from kapitour_shared.clientes_http import ClienteConteudo
from kapitour_shared.contratos.clientes_http import ContratoClienteConteudo


class ServicoFavoritos:
    """SRP: montagem de favoritos com dados de pontos. Cliente HTTP injetado (DIP)."""

    def __init__(
        self,
        favoritos: RepositorioFavorito | None = None,
        conteudo: ContratoClienteConteudo | None = None,
        sessao=None,
    ):
        if favoritos is None:
            if sessao is None:
                raise ValueError("Informe favoritos ou sessao.")
            favoritos = RepositorioFavorito(sessao)
        self.favoritos = favoritos
        self.conteudo = conteudo or ClienteConteudo()

    def listar_com_pontos(self, usuario_id: int) -> list[dict]:
        favoritos = self.favoritos.listar_por_usuario(usuario_id)
        ids_pontos = [fav.ponto_id for fav in favoritos]
        mapa_pontos = {p["id"]: p for p in self.conteudo.buscar_pontos_por_ids(ids_pontos)}
        return [self._montar_favorito(fav, mapa_pontos) for fav in favoritos]

    def _montar_favorito(self, favorito, mapa_pontos: dict) -> dict:
        ponto = mapa_pontos.get(favorito.ponto_id)
        return {
            "id": favorito.id,
            "usuario_id": favorito.usuario_id,
            "ponto_id": favorito.ponto_id,
            "data_adicionado": favorito.data_adicionado.isoformat(),
            "pontos_turisticos": self._serializar_ponto(ponto) if ponto else None,
        }

    def _serializar_ponto(self, ponto: dict) -> dict:
        return {
            "id": ponto["id"],
            "nome": ponto["nome"],
            "descricao": ponto.get("descricao"),
            "latitude": ponto.get("latitude"),
            "longitude": ponto.get("longitude"),
            "url_img": ponto.get("url_img"),
            "rua_numero": ponto.get("rua_numero"),
        }
