from abc import ABC, abstractmethod
from datetime import date

from app.dominio.regras.contexto import ContextoResgateCupom


class ValidadorResgateCupom(ABC):
    """OCP: novas regras estendem esta classe sem alterar ServicoCupom."""

    @abstractmethod
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        """Retorna erro `{success: False, error: ...}` ou None se válido."""


class ValidadorJaResgatado(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        if contexto.repositorio.ja_resgatado(contexto.cupom_id, contexto.usuario_id):
            return {"success": False, "error": "Cupom já resgatado"}
        return None


class ValidadorCupomExiste(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        cupom = contexto.repositorio.buscar_por_id(contexto.cupom_id)
        if not cupom:
            return {"success": False, "error": "Cupom não encontrado"}
        contexto.cupom = cupom
        return None


class ValidadorCupomParceiro(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        if not contexto.parceiro_id or not contexto.cupom:
            return None
        if contexto.cupom.parceiro_id != contexto.parceiro_id:
            return {"success": False, "error": "Cupom não pertence a esta loja/parceiro."}
        return None


class ValidadorCupomDisponivel(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        if contexto.cupom and contexto.cupom.quantidade_disponivel <= 0:
            return {"success": False, "error": "Cupom não disponível"}
        return None


class ValidadorCupomExpirado(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        if (
            contexto.cupom
            and contexto.cupom.data_validade
            and date.today() > contexto.cupom.data_validade
        ):
            return {"success": False, "error": "Cupom expirado"}
        return None


class ValidadorCampanhaAtiva(ValidadorResgateCupom):
    def validar(self, contexto: ContextoResgateCupom) -> dict | None:
        if not contexto.cupom or not contexto.cupom.campanha_id:
            return None

        campanha = contexto.repositorio.buscar_campanha(contexto.cupom.campanha_id)
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
