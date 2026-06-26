from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories import (
    CollectionRepository,
    DiaryRepository,
    EcoRepository,
    KapiPassRepository,
    MissionRepository,
    RankingRepository,
    TreasureRepository,
)
from kapitour_shared.clients import AuthClient, ContentClient
from kapitour_shared.utils import DEFAULT_CHECKIN_RADIUS_M, haversine_m

CONQUISTA_CRITERIOS = {
    "explorador_marica": lambda s: s["visitados"] >= 1,
    "cacador_historias": lambda s: s["visitados"] >= 3,
    "fotografo_urbano": lambda s: s["visitados"] >= 5,
    "guardiao_natureza": lambda s: s["visitados"] >= 8,
    "colecionador_carimbos": lambda s: s["carimbos"] >= 5,
}


class GamificationService:
    def __init__(self, db: Session):
        self.db = db
        self.kapipass = KapiPassRepository(db)
        self.content = ContentClient()
        self.auth = AuthClient()
        self.missions = MissionRepository(db)
        self.diary = DiaryRepository(db)

    def _stats(self, usuario_id: int) -> dict:
        return {
            "visitados": self.kapipass.count_pontos_visitados(usuario_id),
            "carimbos": self.kapipass.count_carimbos(usuario_id),
            "conquistas": self.kapipass.count_conquistas(usuario_id),
        }

    def conceder_xp(self, usuario_id: int, quantidade: int) -> dict:
        registro = self.kapipass.get_or_create_usuario_xp(usuario_id)
        nivel_anterior = registro.nivel_atual
        registro.xp_total += max(0, quantidade)
        nivel = self.kapipass.nivel_para_xp(registro.xp_total)
        if nivel:
            registro.nivel_atual = nivel.ordem
        self.kapipass.salvar_usuario_xp(registro)
        return {
            "xp_total": registro.xp_total,
            "nivel_atual": registro.nivel_atual,
            "subiu_nivel": registro.nivel_atual > nivel_anterior,
        }

    def avaliar_conquistas(self, usuario_id: int) -> list[dict]:
        stats = self._stats(usuario_id)
        novas: list[dict] = []
        for conquista in self.kapipass.list_conquistas():
            criterio = CONQUISTA_CRITERIOS.get(conquista.codigo)
            if not criterio:
                continue
            if self.kapipass.tem_conquista(usuario_id, conquista.id):
                continue
            if criterio(stats):
                self.kapipass.conceder_conquista(usuario_id, conquista.id)
                if conquista.xp_bonus:
                    self.conceder_xp(usuario_id, conquista.xp_bonus)
                novas.append(self._serialize_conquista(conquista, desbloqueada=True))
        return novas

    def avaliar_missoes(self, usuario_id: int) -> list[dict]:
        stats = self._stats(usuario_id)
        concluidas: list[dict] = []
        for registro in self.missions.list_usuario_missoes(usuario_id):
            if registro.concluida:
                continue
            missao = self.missions.get_missao(registro.missao_id)
            if not missao:
                continue
            progresso = stats["carimbos"] if missao.tipo == "carimbos" else stats["visitados"]
            registro.progresso = min(progresso, missao.objetivo_quantidade)
            if registro.progresso >= missao.objetivo_quantidade:
                registro.concluida = True
                registro.data_conclusao = datetime.utcnow()
                self.missions.salvar(registro)
                if missao.xp:
                    self.conceder_xp(usuario_id, missao.xp)
                concluidas.append({"id": missao.id, "nome": missao.nome, "xp": missao.xp})
            else:
                self.missions.salvar(registro)
        return concluidas

    def processar_checkin(
        self,
        usuario_id: int,
        ponto_id: int,
        latitude: float | None,
        longitude: float | None,
        raio_m: int = DEFAULT_CHECKIN_RADIUS_M,
    ) -> dict:
        ponto = self.content.get_ponto(ponto_id)
        if not ponto:
            raise ValueError("Ponto turístico não encontrado.")

        distancia = None
        if (
            latitude is not None
            and longitude is not None
            and ponto.get("latitude") is not None
            and ponto.get("longitude") is not None
        ):
            distancia = haversine_m(
                latitude, longitude, ponto["latitude"], ponto["longitude"]
            )
            if distancia > raio_m:
                raise ValueError(
                    f"Você está muito longe de {ponto['nome']} para fazer check-in "
                    f"(aprox. {int(distancia)}m). Aproxime-se do local."
                )

        xp_inicial = self.kapipass.get_or_create_usuario_xp(usuario_id)
        xp_antes = xp_inicial.xp_total
        nivel_antes = xp_inicial.nivel_atual

        primeira_visita = not self.kapipass.tem_checkin(usuario_id, ponto_id)
        checkin = self.kapipass.criar_checkin(usuario_id, ponto_id, latitude, longitude)

        novo_carimbo = None
        if primeira_visita:
            carimbo = self.kapipass.get_carimbo_por_ponto(ponto_id)
            if carimbo and not self.kapipass.tem_carimbo(usuario_id, carimbo.id):
                self.kapipass.conceder_carimbo(usuario_id, carimbo.id)
                self.conceder_xp(usuario_id, carimbo.xp_recompensa or 0)
                novo_carimbo = self._serialize_carimbo(carimbo, obtido=True)

        novas_conquistas = self.avaliar_conquistas(usuario_id)
        self.avaliar_missoes(usuario_id)
        if primeira_visita:
            self.diary.create(
                usuario_id=usuario_id,
                ponto_turistico_id=ponto_id,
                checkin_id=checkin.id,
                comentario=f"Visitei {ponto['nome']}.",
                foto=ponto.get("url_img"),
            )
        xp_final = self.kapipass.get_or_create_usuario_xp(usuario_id)

        return {
            "checkin": {
                "id": checkin.id,
                "usuario_id": checkin.usuario_id,
                "ponto_turistico_id": checkin.ponto_turistico_id,
                "data_checkin": checkin.data_checkin.isoformat(),
                "latitude": checkin.latitude,
                "longitude": checkin.longitude,
            },
            "primeira_visita": primeira_visita,
            "distancia_m": int(distancia) if distancia is not None else None,
            "xp_ganho": xp_final.xp_total - xp_antes,
            "xp_total": xp_final.xp_total,
            "nivel_atual": xp_final.nivel_atual,
            "subiu_nivel": xp_final.nivel_atual > nivel_antes,
            "novo_carimbo": novo_carimbo,
            "novas_conquistas": novas_conquistas,
            "mensagem": "Check-in realizado com sucesso!"
            if primeira_visita
            else "Visita registrada! Você já coletou o carimbo deste local.",
        }

    def get_passaporte(self, usuario_id: int) -> dict:
        user = self.auth.get_user(usuario_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        registro = self.kapipass.get_or_create_usuario_xp(usuario_id)
        nivel = self.kapipass.nivel_para_xp(registro.xp_total)
        proximo = self.kapipass.proximo_nivel(registro.xp_total)

        xp_total = registro.xp_total
        xp_nivel_atual = nivel.xp_minimo if nivel else 0
        xp_proximo = proximo.xp_minimo if proximo else xp_total
        faixa = max(1, xp_proximo - xp_nivel_atual)
        progresso_nivel = min(100, round(((xp_total - xp_nivel_atual) / faixa) * 100)) if proximo else 100

        total_carimbos = len(self.kapipass.list_carimbos())
        carimbos_obtidos = self.kapipass.count_carimbos(usuario_id)
        total_conquistas = len(self.kapipass.list_conquistas())
        conquistas_obtidas = self.kapipass.count_conquistas(usuario_id)
        visitados = self.kapipass.count_pontos_visitados(usuario_id)

        progresso_geral = round(
            (
                (carimbos_obtidos / total_carimbos if total_carimbos else 0)
                + (conquistas_obtidas / total_conquistas if total_conquistas else 0)
            )
            / 2
            * 100
        )

        return {
            "usuario": {
                "id": user["id"],
                "nome": user["nome"],
                "email": user["email"],
            },
            "nivel": {
                "atual": registro.nivel_atual,
                "nome": nivel.nome if nivel else "Turista Iniciante",
                "proximo_nome": proximo.nome if proximo else None,
            },
            "xp": {
                "total": xp_total,
                "nivel_minimo": xp_nivel_atual,
                "proximo_nivel": xp_proximo,
                "progresso_nivel": progresso_nivel,
            },
            "locais_visitados": visitados,
            "carimbos": {"obtidos": carimbos_obtidos, "total": total_carimbos},
            "conquistas": {"obtidas": conquistas_obtidas, "total": total_conquistas},
            "progresso_geral": progresso_geral,
        }

    def list_niveis(self) -> list[dict]:
        return [
            {"id": n.id, "nome": n.nome, "xp_minimo": n.xp_minimo, "ordem": n.ordem}
            for n in self.kapipass.list_niveis()
        ]

    def list_carimbos(self, usuario_id: int) -> list[dict]:
        obtidos = {uc.carimbo_id: uc for uc in self.kapipass.list_usuario_carimbos(usuario_id)}
        resultado = []
        for carimbo in self.kapipass.list_carimbos():
            uc = obtidos.get(carimbo.id)
            data = self._serialize_carimbo(carimbo, obtido=uc is not None)
            data["data_obtencao"] = uc.data_obtencao.isoformat() if uc else None
            resultado.append(data)
        return resultado

    def list_conquistas(self, usuario_id: int) -> list[dict]:
        obtidas = {uc.conquista_id: uc for uc in self.kapipass.list_usuario_conquistas(usuario_id)}
        resultado = []
        for conquista in self.kapipass.list_conquistas():
            uc = obtidas.get(conquista.id)
            data = self._serialize_conquista(conquista, desbloqueada=uc is not None)
            data["data_desbloqueio"] = uc.data_desbloqueio.isoformat() if uc else None
            resultado.append(data)
        return resultado

    def list_checkins(self, usuario_id: int) -> list[dict]:
        checkins = self.kapipass.list_checkins(usuario_id)
        ponto_ids = [c.ponto_turistico_id for c in checkins]
        pontos_map = {p["id"]: p for p in self.content.get_pontos_by_ids(ponto_ids)}
        resultado = []
        for checkin in checkins:
            ponto = pontos_map.get(checkin.ponto_turistico_id)
            resultado.append(
                {
                    "id": checkin.id,
                    "usuario_id": checkin.usuario_id,
                    "ponto_turistico_id": checkin.ponto_turistico_id,
                    "data_checkin": checkin.data_checkin.isoformat(),
                    "latitude": checkin.latitude,
                    "longitude": checkin.longitude,
                    "ponto_nome": ponto["nome"] if ponto else None,
                }
            )
        return resultado

    def _serialize_carimbo(self, carimbo, obtido: bool) -> dict:
        return {
            "id": carimbo.id,
            "ponto_turistico_id": carimbo.ponto_turistico_id,
            "nome": carimbo.nome,
            "descricao": carimbo.descricao,
            "imagem": carimbo.imagem,
            "raridade": carimbo.raridade,
            "xp_recompensa": carimbo.xp_recompensa,
            "obtido": obtido,
        }

    def _serialize_conquista(self, conquista, desbloqueada: bool) -> dict:
        return {
            "id": conquista.id,
            "codigo": conquista.codigo,
            "nome": conquista.nome,
            "descricao": conquista.descricao,
            "icone": conquista.icone,
            "xp_bonus": conquista.xp_bonus,
            "desbloqueada": desbloqueada,
        }


class CollectionService:
    def __init__(self, db: Session):
        self.collections = CollectionRepository(db)
        self.kapipass = KapiPassRepository(db)
        self.content = ContentClient()

    def list_colecoes(self, usuario_id: int) -> list[dict]:
        visitados = {c.ponto_turistico_id for c in self.kapipass.list_checkins(usuario_id)}
        resultado = []
        for colecao in self.collections.list_colecoes():
            ponto_ids = self.collections.list_pontos_da_colecao(colecao.id)
            total = len(ponto_ids)
            concluidos = sum(1 for pid in ponto_ids if pid in visitados)
            percentual = round((concluidos / total) * 100) if total else 0
            pontos = []
            for ponto in self.content.get_pontos_by_ids(ponto_ids):
                pontos.append(
                    {
                        "id": ponto["id"],
                        "nome": ponto["nome"],
                        "url_img": ponto.get("url_img"),
                        "visitado": ponto["id"] in visitados,
                    }
                )
            resultado.append(
                {
                    "id": colecao.id,
                    "nome": colecao.nome,
                    "descricao": colecao.descricao,
                    "imagem": colecao.imagem,
                    "total": total,
                    "concluidos": concluidos,
                    "percentual": percentual,
                    "pontos": pontos,
                }
            )
        return resultado


class MissionService:
    def __init__(self, db: Session):
        self.missions = MissionRepository(db)
        self.gamification = GamificationService(db)

    def list_missoes(self, usuario_id: int) -> list[dict]:
        self.gamification.avaliar_missoes(usuario_id)
        aceitas = {m.missao_id: m for m in self.missions.list_usuario_missoes(usuario_id)}
        resultado = []
        for missao in self.missions.list_ativas():
            registro = aceitas.get(missao.id)
            resultado.append(
                {
                    "id": missao.id,
                    "nome": missao.nome,
                    "descricao": missao.descricao,
                    "tipo": missao.tipo,
                    "objetivo_quantidade": missao.objetivo_quantidade,
                    "xp": missao.xp,
                    "recompensa": missao.recompensa,
                    "dias_validade": missao.dias_validade,
                    "aceita": registro is not None,
                    "progresso": registro.progresso if registro else 0,
                    "concluida": registro.concluida if registro else False,
                }
            )
        return resultado

    def aceitar(self, usuario_id: int, missao_id: int) -> dict:
        missao = self.missions.get_missao(missao_id)
        if not missao or not missao.ativo:
            raise ValueError("Missão não encontrada ou inativa.")
        if self.missions.get_usuario_missao(usuario_id, missao_id):
            raise ValueError("Você já aceitou esta missão.")
        self.missions.aceitar(usuario_id, missao_id)
        self.gamification.avaliar_missoes(usuario_id)
        return {"success": True, "message": "Missão aceita!"}


class EcoService:
    def __init__(self, db: Session):
        self.eco = EcoRepository(db)
        self.gamification = GamificationService(db)

    def list_atividades(self, usuario_id: int) -> dict:
        registradas = {}
        for r in self.eco.list_usuario_atividades(usuario_id):
            registradas[r.eco_atividade_id] = registradas.get(r.eco_atividade_id, 0) + 1
        atividades = []
        for atividade in self.eco.list_atividades():
            atividades.append(
                {
                    "id": atividade.id,
                    "nome": atividade.nome,
                    "descricao": atividade.descricao,
                    "tipo": atividade.tipo,
                    "pontuacao_eco": atividade.pontuacao_eco,
                    "xp_recompensa": atividade.xp_recompensa,
                    "vezes_registrada": registradas.get(atividade.id, 0),
                }
            )
        return {
            "pontuacao_eco_total": self.eco.pontuacao_total(usuario_id),
            "atividades": atividades,
        }

    def registrar(self, usuario_id: int, atividade_id: int) -> dict:
        atividade = self.eco.get_atividade(atividade_id)
        if not atividade:
            raise ValueError("Atividade ecológica não encontrada.")
        self.eco.registrar(usuario_id, atividade_id, atividade.pontuacao_eco or 0)
        if atividade.xp_recompensa:
            self.gamification.conceder_xp(usuario_id, atividade.xp_recompensa)
        return {
            "success": True,
            "message": f"Atividade registrada! +{atividade.pontuacao_eco} EcoPontos.",
            "pontuacao_eco_total": self.eco.pontuacao_total(usuario_id),
        }


class DiaryService:
    def __init__(self, db: Session):
        self.diary = DiaryRepository(db)
        self.content = ContentClient()

    def list_entradas(self, usuario_id: int) -> list[dict]:
        resultado = []
        entradas = self.diary.list_by_user(usuario_id)
        ponto_ids = [e.ponto_turistico_id for e in entradas if e.ponto_turistico_id]
        pontos_map = {p["id"]: p for p in self.content.get_pontos_by_ids(ponto_ids)}
        for entrada in entradas:
            ponto = pontos_map.get(entrada.ponto_turistico_id) if entrada.ponto_turistico_id else None
            resultado.append(
                {
                    "id": entrada.id,
                    "usuario_id": entrada.usuario_id,
                    "ponto_turistico_id": entrada.ponto_turistico_id,
                    "ponto_nome": ponto["nome"] if ponto else None,
                    "checkin_id": entrada.checkin_id,
                    "comentario": entrada.comentario,
                    "foto": entrada.foto,
                    "data": entrada.data.isoformat(),
                }
            )
        return resultado

    def criar(
        self,
        usuario_id: int,
        ponto_turistico_id: int | None,
        checkin_id: int | None,
        comentario: str | None,
        foto: str | None,
    ) -> dict:
        entrada = self.diary.create(usuario_id, ponto_turistico_id, checkin_id, comentario, foto)
        return {
            "id": entrada.id,
            "usuario_id": entrada.usuario_id,
            "ponto_turistico_id": entrada.ponto_turistico_id,
            "checkin_id": entrada.checkin_id,
            "comentario": entrada.comentario,
            "foto": entrada.foto,
            "data": entrada.data.isoformat(),
        }


class TreasureService:
    def __init__(self, db: Session):
        self.treasures = TreasureRepository(db)
        self.kapipass = KapiPassRepository(db)
        self.gamification = GamificationService(db)

    def list_tesouros(self, usuario_id: int) -> list[dict]:
        concluidos = {t.tesouro_id for t in self.treasures.list_usuario_tesouros(usuario_id)}
        resultado = []
        for tesouro in self.treasures.list_tesouros():
            concluido = tesouro.id in concluidos
            resultado.append(
                {
                    "id": tesouro.id,
                    "nome": tesouro.nome,
                    "descricao": tesouro.descricao,
                    "pista": tesouro.pista,
                    "enigma": tesouro.enigma if concluido else None,
                    "ponto_turistico_id": tesouro.ponto_turistico_id,
                    "xp_bonus": tesouro.xp_bonus,
                    "concluido": concluido,
                }
            )
        return resultado

    def concluir(self, usuario_id: int, tesouro_id: int) -> dict:
        tesouro = self.treasures.get_tesouro(tesouro_id)
        if not tesouro:
            raise ValueError("Tesouro não encontrado.")
        if self.treasures.ja_concluido(usuario_id, tesouro_id):
            raise ValueError("Você já concluiu este tesouro.")
        self.treasures.concluir(usuario_id, tesouro_id)

        recompensas = []
        if tesouro.carimbo_id and not self.kapipass.tem_carimbo(usuario_id, tesouro.carimbo_id):
            self.kapipass.conceder_carimbo(usuario_id, tesouro.carimbo_id)
            recompensas.append("carimbo especial")
        if tesouro.conquista_id and not self.kapipass.tem_conquista(usuario_id, tesouro.conquista_id):
            self.kapipass.conceder_conquista(usuario_id, tesouro.conquista_id)
            recompensas.append("conquista especial")
        if tesouro.xp_bonus:
            self.gamification.conceder_xp(usuario_id, tesouro.xp_bonus)
            recompensas.append(f"+{tesouro.xp_bonus} XP")

        return {
            "success": True,
            "message": "Tesouro encontrado!",
            "recompensas": recompensas,
        }


class RankingService:
    CATEGORIAS = {"exploradores", "trilheiros", "colecionadores", "ecopass", "xp"}

    def __init__(self, db: Session):
        self.rankings = RankingRepository(db)
        self.auth = AuthClient()

    def get_ranking(self, categoria: str, page: int = 1, size: int = 20) -> dict:
        categoria = (categoria or "exploradores").lower()
        page = max(1, page)
        size = max(1, min(size, 100))

        if categoria == "colecionadores":
            linhas = self.rankings.ranking_carimbos(page, size)
            unidade = "carimbos"
        elif categoria == "ecopass":
            linhas = self.rankings.ranking_eco(page, size)
            unidade = "ecopontos"
        elif categoria == "xp":
            linhas = self.rankings.ranking_xp(page, size)
            unidade = "xp"
        else:
            linhas = self.rankings.ranking_checkins(page, size)
            unidade = "locais"

        user_ids = [int(row[0]) for row in linhas]
        users_map = self.auth.batch_users(user_ids)
        inicio = (page - 1) * size
        itens = []
        for i, row in enumerate(linhas):
            usuario_id = int(row[0])
            user = users_map.get(usuario_id)
            itens.append(
                {
                    "posicao": inicio + i + 1,
                    "usuario_id": usuario_id,
                    "nome": user["nome"] if user else f"Usuário {usuario_id}",
                    "valor": int(row[1] if categoria == "xp" else row[1]),
                    "unidade": unidade,
                }
            )
        return {"categoria": categoria, "page": page, "size": size, "itens": itens}
