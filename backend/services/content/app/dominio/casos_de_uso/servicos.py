from app.infraestrutura.persistencia.repositorios import RepositorioCategoria, RepositorioPonto, RepositorioRota


class CasoListarCategorias:
    def __init__(self, repositorio: RepositorioCategoria):
        self._categorias = repositorio

    def listar(self):
        return self._categorias.listar_todos()


class CasoListarPontos:
    def __init__(self, repositorio: RepositorioPonto):
        self._pontos = repositorio

    def listar(self, categoria_id: int | None = None):
        return self._pontos.listar_todos(categoria_id)

    def buscar_por_id(self, ponto_id: int):
        return self._pontos.buscar_por_id(ponto_id)

    def buscar_por_ids(self, ids: list[int]):
        return self._pontos.buscar_por_ids(ids)

    def listar_ponto_categoria(
        self,
        ponto_id: int | None = None,
        categoria_id: int | None = None,
        ponto_ids: list[int] | None = None,
    ) -> list[dict]:
        if ponto_id:
            linhas = self._pontos.buscar_ponto_categorias([ponto_id])
        elif ponto_ids:
            linhas = self._pontos.buscar_ponto_categorias(ponto_ids)
        elif categoria_id:
            linhas = self._pontos.buscar_ponto_categorias_por_categoria(categoria_id)
        else:
            linhas = []
        return [{"ponto_id": linha.ponto_id, "categoria_id": linha.categoria_id} for linha in linhas]


class CasoListarRotas:
    def __init__(self, repositorio_rota: RepositorioRota, repositorio_ponto: RepositorioPonto):
        self._rotas = repositorio_rota
        self._pontos = repositorio_ponto

    def listar(self):
        return self._rotas.listar_todos()

    def pontos_da_rota(self, rota_id: int):
        relacoes = self._rotas.buscar_rota_pontos(rota_id)
        ids_pontos = [r.ponto_id for r in relacoes]
        pontos = self._pontos.buscar_por_ids(ids_pontos)
        return relacoes, ids_pontos, pontos

    def listar_rota_ponto(self, rota_id: int | None = None, ponto_ids: list[int] | None = None):
        if rota_id:
            return self._rotas.buscar_rota_pontos(rota_id)
        if ponto_ids:
            return self._rotas.buscar_rota_pontos_por_ponto_ids(ponto_ids)
        return []


# Aliases de compatibilidade
ServicoCategorias = CasoListarCategorias
ServicoPontos = CasoListarPontos
ServicoRotas = CasoListarRotas
