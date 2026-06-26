from datetime import datetime
from types import SimpleNamespace


class RepositorioFavoritoFake:
    def __init__(self):
        self._favoritos = [
            SimpleNamespace(
                id=1,
                usuario_id=10,
                ponto_id=100,
                data_adicionado=datetime(2024, 6, 1, 12, 0, 0),
            ),
            SimpleNamespace(
                id=2,
                usuario_id=10,
                ponto_id=101,
                data_adicionado=datetime(2024, 6, 2, 12, 0, 0),
            ),
        ]

    def listar_por_usuario(self, usuario_id):
        return [f for f in self._favoritos if f.usuario_id == usuario_id]


class ClienteConteudoFake:
    def __init__(self, pontos=None):
        self._pontos = pontos or {
            100: {
                "id": 100,
                "nome": "Praia",
                "descricao": "Mar",
                "latitude": -22.9,
                "longitude": -42.8,
                "url_img": None,
                "rua_numero": "Rua 1",
            },
            101: {
                "id": 101,
                "nome": "Museu",
                "descricao": "História",
                "latitude": -22.91,
                "longitude": -42.81,
                "url_img": None,
                "rua_numero": "Rua 2",
            },
        }

    def buscar_pontos_por_ids(self, ids):
        return [self._pontos[i] for i in ids if i in self._pontos]


class RepositorioAvaliacaoFake:
    def __init__(self):
        self._avaliacoes = []

    def listar_por_ponto(self, ponto_id):
        return [a for a in self._avaliacoes if a.ponto_id == ponto_id]

    def buscar_avaliacao_usuario(self, usuario_id, ponto_id):
        for a in self._avaliacoes:
            if a.usuario_id == usuario_id and a.ponto_id == ponto_id:
                return a
        return None

    def criar(self, usuario_id, ponto_id, nota, comentario):
        avaliacao = SimpleNamespace(
            id=len(self._avaliacoes) + 1,
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            nota=nota,
            comentario=comentario,
        )
        self._avaliacoes.append(avaliacao)
        return avaliacao

    def atualizar(self, avaliacao, nota, comentario):
        avaliacao.nota = nota
        avaliacao.comentario = comentario
        return avaliacao

    def buscar_por_id(self, avaliacao_id):
        return next((a for a in self._avaliacoes if a.id == avaliacao_id), None)

    def listar_ponto_avaliacoes(self, ponto_id):
        return [a for a in self._avaliacoes if a.ponto_id == ponto_id]

    def criar_ponto_avaliacao(self, ponto_id, usuario_id, nota, comentario):
        return self.criar(usuario_id or 0, ponto_id, nota, comentario)
