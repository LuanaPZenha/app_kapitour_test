"""Testes do helper de paginação."""

from kapitour_shared.core.paginacao import montar_resposta_paginada, paginar


class TestPaginacao:
    def test_paginar_primeira_pagina(self):
        itens = list(range(25))
        fatia, total = paginar(itens, pagina=1, tamanho=10)
        assert fatia == list(range(10))
        assert total == 25

    def test_montar_resposta_total_paginas(self):
        resposta = montar_resposta_paginada(list(range(25)), pagina=3, tamanho=10)
        assert resposta["itens"] == [20, 21, 22, 23, 24]
        assert resposta["total"] == 25
        assert resposta["total_paginas"] == 3
