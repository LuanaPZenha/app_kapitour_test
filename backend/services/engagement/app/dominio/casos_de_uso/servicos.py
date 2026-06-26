from app.infraestrutura.persistencia.repositorios import RepositorioAvaliacao, RepositorioFavorito
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


class ServicoAvaliacao:
    """Repository: regras de avaliação delegadas ao repositório."""

    def __init__(self, repositorio: RepositorioAvaliacao):
        self._avaliacoes = repositorio

    def listar(self, ponto_id: int | None = None, usuario_id: int | None = None):
        if usuario_id and ponto_id:
            return self._avaliacoes.buscar_avaliacao_usuario(usuario_id, ponto_id)
        if ponto_id:
            return self._avaliacoes.listar_por_ponto(ponto_id)
        return []

    def criar_ou_atualizar(self, usuario_id: int, ponto_id: int, nota: int, comentario: str | None):
        existente = self._avaliacoes.buscar_avaliacao_usuario(usuario_id, ponto_id)
        if existente:
            return self._avaliacoes.atualizar(existente, nota, comentario)
        return self._avaliacoes.criar(usuario_id, ponto_id, nota, comentario)

    def atualizar_por_id(self, avaliacao_id: int, nota: int, comentario: str | None):
        avaliacao = self._avaliacoes.buscar_por_id(avaliacao_id)
        if not avaliacao:
            return None
        return self._avaliacoes.atualizar(avaliacao, nota, comentario)

    def criar_ponto_avaliacao(
        self, ponto_id: int, usuario_id: int | None, nota: int, comentario: str | None
    ):
        return self._avaliacoes.criar_ponto_avaliacao(ponto_id, usuario_id, nota, comentario)

    def media_por_ponto(self, ponto_id: int) -> dict:
        avaliacoes = self._avaliacoes.listar_ponto_avaliacoes(ponto_id)
        if not avaliacoes:
            return {"media": 0}
        media = sum(a.nota for a in avaliacoes) / len(avaliacoes)
        return {"media": round(media, 1)}
