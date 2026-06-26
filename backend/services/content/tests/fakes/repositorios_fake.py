from types import SimpleNamespace


class RepositorioPontoFake:
    def __init__(self, pontos: list | None = None):
        self._pontos = pontos or [
            SimpleNamespace(id=1, nome="Praia de Itaipuaçu", categoria_id=1),
            SimpleNamespace(id=2, nome="Centro Histórico", categoria_id=2),
        ]

    def listar_todos(self, categoria_id=None):
        if categoria_id is None:
            return self._pontos
        return [p for p in self._pontos if p.categoria_id == categoria_id]

    def buscar_por_id(self, ponto_id):
        return next((p for p in self._pontos if p.id == ponto_id), None)

    def buscar_por_ids(self, ids):
        return [p for p in self._pontos if p.id in ids]

    def buscar_ponto_categorias(self, ponto_ids):
        return [
            SimpleNamespace(ponto_id=pid, categoria_id=1)
            for pid in ponto_ids
        ]

    def buscar_ponto_categorias_por_categoria(self, categoria_id):
        return [
            SimpleNamespace(ponto_id=p.id, categoria_id=p.categoria_id)
            for p in self._pontos
            if p.categoria_id == categoria_id
        ]


class RepositorioCategoriaFake:
    def __init__(self):
        self._categorias = [
            SimpleNamespace(id=1, nome="Praias"),
            SimpleNamespace(id=2, nome="História"),
        ]

    def listar_todos(self):
        return self._categorias


class RepositorioRotaFake:
    def __init__(self):
        self._rotas = [SimpleNamespace(id=10, nome="Rota Litorânea")]
        self._rota_pontos = [
            SimpleNamespace(rota_id=10, ponto_id=1, ordem=1),
            SimpleNamespace(rota_id=10, ponto_id=2, ordem=2),
        ]

    def listar_todos(self):
        return self._rotas

    def buscar_rota_pontos(self, rota_id):
        return [r for r in self._rota_pontos if r.rota_id == rota_id]

    def buscar_rota_pontos_por_ponto_ids(self, ponto_ids):
        return [r for r in self._rota_pontos if r.ponto_id in ponto_ids]
