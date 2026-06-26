from app.infraestrutura.persistencia.modelos import Campanha, Cupom
from app.infraestrutura.persistencia.repositorios import RepositorioCupom
from app.dominio.regras import CadeiaValidacaoResgateCupom, ContextoResgateCupom


class ServicoCupom:
    """SRP: orquestra listagem e resgate; validação delegada à cadeia (OCP)."""

    def __init__(
        self,
        repositorio: RepositorioCupom,
        cadeia_validacao: CadeiaValidacaoResgateCupom | None = None,
    ):
        self._cupons = repositorio
        if cadeia_validacao is None:
            from app.apresentacao.dependencias import obter_cadeia_validacao_resgate

            cadeia_validacao = obter_cadeia_validacao_resgate()
        self._cadeia = cadeia_validacao

    def listar_disponiveis(self, parceiro_id: int | None = None) -> list[dict]:
        cupons = self._cupons.listar_disponiveis(parceiro_id)
        return [self._montar_cupom_com_campanha(cupom) for cupom in cupons]

    def listar_resgatados(self, usuario_id: int) -> list[dict]:
        resgates = self._cupons.listar_resgatados(usuario_id)
        return [self._montar_resgate(resgate) for resgate in resgates]

    def resgatar(self, cupom_id: int, usuario_id: int, parceiro_id: int | None = None) -> dict:
        erro = self._validar_resgate(cupom_id, usuario_id, parceiro_id)
        if erro:
            return erro

        cupom = self._cupons.buscar_por_id(cupom_id)
        self._cupons.resgatar(cupom, usuario_id)
        return {"success": True, "message": "Cupom resgatado com sucesso!"}

    def campanhas_parceiro(self, parceiro_id: int) -> list[dict]:
        cupons = self._cupons.listar_por_parceiro(parceiro_id)
        campanhas_map = {}
        for cupom in cupons:
            if cupom.campanha_id and cupom.campanha_id not in campanhas_map:
                campanha = self._cupons.buscar_campanha(cupom.campanha_id)
                if campanha:
                    campanhas_map[campanha.id] = campanha
        return [self._serializar_campanha(c) for c in campanhas_map.values()]

    def contagem_por_campanha(self, parceiro_id: int) -> dict:
        cupons = self._cupons.listar_por_parceiro(parceiro_id)
        contagem = {}
        for cupom in cupons:
            chave = str(cupom.campanha_id or 0)
            contagem[chave] = contagem.get(chave, 0) + (cupom.quantidade_disponivel or 0)
        return contagem

    def _montar_cupom_com_campanha(self, cupom: Cupom) -> dict:
        campanha = None
        if cupom.campanha_id:
            campanha = self._cupons.buscar_campanha(cupom.campanha_id)
        return self._serializar_cupom(cupom, campanha)

    def _montar_resgate(self, resgate) -> dict:
        cupom = self._cupons.buscar_por_id(resgate.cupom_id)
        campanha = (
            self._cupons.buscar_campanha(cupom.campanha_id)
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
        contexto = ContextoResgateCupom(
            cupom_id=cupom_id,
            usuario_id=usuario_id,
            parceiro_id=parceiro_id,
            repositorio=self._cupons,
        )
        return self._cadeia.validar(contexto)

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
