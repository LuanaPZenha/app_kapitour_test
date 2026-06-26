from datetime import date

from sqlalchemy.orm import Session

from app.modelos import Campanha, Cupom
from app.repositorios import RepositorioCupom


class ServicoCupom:
    def __init__(self, sessao: Session):
        self.cupons = RepositorioCupom(sessao)

    def listar_disponiveis(self, parceiro_id: int | None = None) -> list[dict]:
        cupons = self.cupons.listar_disponiveis(parceiro_id)
        return [self._montar_cupom_com_campanha(cupom) for cupom in cupons]

    def listar_resgatados(self, usuario_id: int) -> list[dict]:
        resgates = self.cupons.listar_resgatados(usuario_id)
        return [self._montar_resgate(resgate) for resgate in resgates]

    def resgatar(self, cupom_id: int, usuario_id: int, parceiro_id: int | None = None) -> dict:
        erro = self._validar_resgate(cupom_id, usuario_id, parceiro_id)
        if erro:
            return erro

        cupom = self.cupons.buscar_por_id(cupom_id)
        self.cupons.resgatar(cupom, usuario_id)
        return {"success": True, "message": "Cupom resgatado com sucesso!"}

    def campanhas_parceiro(self, parceiro_id: int) -> list[dict]:
        cupons = self.cupons.listar_por_parceiro(parceiro_id)
        campanhas_map = {}
        for cupom in cupons:
            if cupom.campanha_id and cupom.campanha_id not in campanhas_map:
                campanha = self.cupons.buscar_campanha(cupom.campanha_id)
                if campanha:
                    campanhas_map[campanha.id] = campanha
        return [self._serializar_campanha(c) for c in campanhas_map.values()]

    def contagem_por_campanha(self, parceiro_id: int) -> dict:
        cupons = self.cupons.listar_por_parceiro(parceiro_id)
        contagem = {}
        for cupom in cupons:
            chave = str(cupom.campanha_id or 0)
            contagem[chave] = contagem.get(chave, 0) + (cupom.quantidade_disponivel or 0)
        return contagem

    def _montar_cupom_com_campanha(self, cupom: Cupom) -> dict:
        campanha = None
        if cupom.campanha_id:
            campanha = self.cupons.buscar_campanha(cupom.campanha_id)
        return self._serializar_cupom(cupom, campanha)

    def _montar_resgate(self, resgate) -> dict:
        cupom = self.cupons.buscar_por_id(resgate.cupom_id)
        campanha = (
            self.cupons.buscar_campanha(cupom.campanha_id)
            if cupom and cupom.campanha_id
            else None
        )
        return {
            "id": resgate.id,
            "data_resgate": resgate.data_resgate.isoformat(),
            "cupom": self._serializar_cupom(cupom, campanha) if cupom else None,
        }

    def _validar_resgate(
        self, cupom_id: int, usuario_id: int, parceiro_id: int | None
    ) -> dict | None:
        if self.cupons.ja_resgatado(cupom_id, usuario_id):
            return {"success": False, "error": "Cupom já resgatado"}

        cupom = self.cupons.buscar_por_id(cupom_id)
        if not cupom:
            return {"success": False, "error": "Cupom não encontrado"}
        if parceiro_id and cupom.parceiro_id != parceiro_id:
            return {"success": False, "error": "Cupom não pertence a esta loja/parceiro."}
        if cupom.quantidade_disponivel <= 0:
            return {"success": False, "error": "Cupom não disponível"}
        if cupom.data_validade and date.today() > cupom.data_validade:
            return {"success": False, "error": "Cupom expirado"}

        if cupom.campanha_id:
            erro_campanha = self._validar_campanha(cupom.campanha_id)
            if erro_campanha:
                return erro_campanha

        return None

    def _validar_campanha(self, campanha_id: int) -> dict | None:
        campanha = self.cupons.buscar_campanha(campanha_id)
        if not campanha:
            return None
        hoje = date.today()
        if campanha.ativa is False:
            return {"success": False, "error": "Campanha inativa"}
        if campanha.data_inicio and hoje < campanha.data_inicio:
            return {"success": False, "error": "Campanha ainda não começou"}
        if campanha.data_fim and hoje > campanha.data_fim:
            return {"success": False, "error": "Campanha encerrada"}
        return None

    def _serializar_campanha(self, campanha: Campanha) -> dict:
        return {
            "id": campanha.id,
            "nome": campanha.nome,
            "descricao": campanha.descricao,
            "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
            "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None,
            "ativa": campanha.ativa,
            "criada_em": campanha.criada_em.isoformat() if campanha.criada_em else None,
        }

    def _serializar_cupom(self, cupom: Cupom, campanha: Campanha | None) -> dict:
        return {
            "id": cupom.id,
            "codigo": cupom.codigo,
            "descricao": cupom.descricao,
            "data_validade": cupom.data_validade.isoformat() if cupom.data_validade else None,
            "quantidade_disponivel": cupom.quantidade_disponivel,
            "campanha_id": cupom.campanha_id,
            "parceiro_id": cupom.parceiro_id,
            "campanha": self._serializar_campanha(campanha) if campanha else None,
        }
