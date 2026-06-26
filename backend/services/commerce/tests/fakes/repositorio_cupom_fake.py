from datetime import date, timedelta
from types import SimpleNamespace


class RepositorioCupomFake:
    """Fake do repositório de cupons para testes de regras de resgate."""

    def __init__(self):
        self.cupons: dict[int, SimpleNamespace] = {}
        self.resgates: set[tuple[int, int]] = set()
        self.campanhas: dict[int, SimpleNamespace] = {}

    def adicionar_cupom(self, cupom_id, **kwargs):
        padrao = {
            "id": cupom_id,
            "codigo": f"CUP{cupom_id}",
            "descricao": "Desconto",
            "parceiro_id": 1,
            "quantidade_disponivel": 10,
            "data_validade": date.today() + timedelta(days=30),
            "campanha_id": None,
        }
        padrao.update(kwargs)
        self.cupons[cupom_id] = SimpleNamespace(**padrao)

    def adicionar_campanha(self, campanha_id, **kwargs):
        padrao = {
            "id": campanha_id,
            "nome": "Campanha Verão",
            "descricao": "",
            "data_inicio": date.today() - timedelta(days=1),
            "data_fim": date.today() + timedelta(days=30),
            "ativa": True,
            "criada_em": None,
        }
        padrao.update(kwargs)
        self.campanhas[campanha_id] = SimpleNamespace(**padrao)

    def ja_resgatado(self, cupom_id, usuario_id):
        return (cupom_id, usuario_id) in self.resgates

    def buscar_por_id(self, cupom_id):
        return self.cupons.get(cupom_id)

    def buscar_campanha(self, campanha_id):
        return self.campanhas.get(campanha_id)

    def resgatar(self, cupom, usuario_id):
        self.resgates.add((cupom.id, usuario_id))
        cupom.quantidade_disponivel -= 1

    def listar_disponiveis(self, parceiro_id=None):
        return list(self.cupons.values())

    def listar_resgatados(self, usuario_id):
        return []

    def listar_por_parceiro(self, parceiro_id):
        return [c for c in self.cupons.values() if c.parceiro_id == parceiro_id]
