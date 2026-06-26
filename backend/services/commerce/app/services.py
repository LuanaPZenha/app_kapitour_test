from datetime import date

from sqlalchemy.orm import Session

from app.models import Campanha, Cupom
from app.repositories import CouponRepository


class CouponService:
    def __init__(self, db: Session):
        self.coupons = CouponRepository(db)

    def list_available(self, parceiro_id: int | None = None) -> list[dict]:
        cupons = self.coupons.list_available(parceiro_id)
        result = []
        for cupom in cupons:
            campanha = None
            if cupom.campanha_id:
                campanha = self.coupons.get_campanha(cupom.campanha_id)
            result.append(self._serialize_cupom(cupom, campanha))
        return result

    def list_resgatados(self, usuario_id: int) -> list[dict]:
        resgates = self.coupons.list_resgatados(usuario_id)
        result = []
        for resgate in resgates:
            cupom = self.coupons.get_by_id(resgate.cupom_id)
            campanha = self.coupons.get_campanha(cupom.campanha_id) if cupom and cupom.campanha_id else None
            result.append(
                {
                    "id": resgate.id,
                    "data_resgate": resgate.data_resgate.isoformat(),
                    "cupom": self._serialize_cupom(cupom, campanha) if cupom else None,
                }
            )
        return result

    def redeem(self, cupom_id: int, usuario_id: int, parceiro_id: int | None = None) -> dict:
        if self.coupons.already_redeemed(cupom_id, usuario_id):
            return {"success": False, "error": "Cupom já resgatado"}

        cupom = self.coupons.get_by_id(cupom_id)
        if not cupom:
            return {"success": False, "error": "Cupom não encontrado"}
        if parceiro_id and cupom.parceiro_id != parceiro_id:
            return {"success": False, "error": "Cupom não pertence a esta loja/parceiro."}
        if cupom.quantidade_disponivel <= 0:
            return {"success": False, "error": "Cupom não disponível"}

        if cupom.campanha_id:
            campanha = self.coupons.get_campanha(cupom.campanha_id)
            if campanha:
                hoje = date.today()
                if campanha.ativa is False:
                    return {"success": False, "error": "Campanha inativa"}
                if campanha.data_inicio and hoje < campanha.data_inicio:
                    return {"success": False, "error": "Campanha ainda não começou"}
                if campanha.data_fim and hoje > campanha.data_fim:
                    return {"success": False, "error": "Campanha encerrada"}

        if cupom.data_validade and date.today() > cupom.data_validade:
            return {"success": False, "error": "Cupom expirado"}

        self.coupons.redeem(cupom, usuario_id)
        return {"success": True, "message": "Cupom resgatado com sucesso!"}

    def campanhas_parceiro(self, parceiro_id: int) -> list[dict]:
        cupons = self.coupons.list_by_parceiro(parceiro_id)
        campanhas_map = {}
        for cupom in cupons:
            if cupom.campanha_id and cupom.campanha_id not in campanhas_map:
                campanha = self.coupons.get_campanha(cupom.campanha_id)
                if campanha:
                    campanhas_map[campanha.id] = campanha
        return [self._serialize_campanha(c) for c in campanhas_map.values()]

    def contagem_por_campanha(self, parceiro_id: int) -> dict:
        cupons = self.coupons.list_by_parceiro(parceiro_id)
        contagem = {}
        for cupom in cupons:
            key = str(cupom.campanha_id or 0)
            contagem[key] = contagem.get(key, 0) + (cupom.quantidade_disponivel or 0)
        return contagem

    def _serialize_campanha(self, campanha: Campanha) -> dict:
        return {
            "id": campanha.id,
            "nome": campanha.nome,
            "descricao": campanha.descricao,
            "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
            "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None,
            "ativa": campanha.ativa,
            "criada_em": campanha.criada_em.isoformat() if campanha.criada_em else None,
        }

    def _serialize_cupom(self, cupom: Cupom, campanha: Campanha | None) -> dict:
        return {
            "id": cupom.id,
            "codigo": cupom.codigo,
            "descricao": cupom.descricao,
            "data_validade": cupom.data_validade.isoformat() if cupom.data_validade else None,
            "quantidade_disponivel": cupom.quantidade_disponivel,
            "campanha_id": cupom.campanha_id,
            "parceiro_id": cupom.parceiro_id,
            "campanha": self._serialize_campanha(campanha) if campanha else None,
        }
