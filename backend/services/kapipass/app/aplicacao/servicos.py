from datetime import datetime

from sqlalchemy.orm import Session

from app.dominio.estrategias.conquistas import REGISTRO_CRITERIOS_CONQUISTA
from app.dominio.estrategias.missoes import ESTRATEGIA_MISSAO_PADRAO, REGISTRO_ESTRATEGIAS_MISSAO
from app.dominio.estrategias.ranking import REGISTRO_ESTRATEGIAS_RANKING
from app.dominio.eventos.publicador import PublicadorEventosCheckin, criar_publicador_checkin_padrao
from app.dominio.eventos.modelo import ContextoCheckin
from app.infraestrutura.persistencia.repositorios import (
    RepositorioColecao,
    RepositorioDiario,
    RepositorioEco,
    RepositorioKapiPass,
    RepositorioMissao,
    RepositorioRanking,
    RepositorioTesouro,
)
from kapitour_shared.clientes_http import ClienteAutenticacao, ClienteConteudo
from kapitour_shared.contratos.clientes_http import (
    ContratoClienteAutenticacao,
    ContratoClienteConteudo,
)
from kapitour_shared.utilitarios import RAIO_PADRAO_CHECKIN_METROS, calcular_distancia_haversine_metros


class ServicoGamificacao:
    """SRP: gamificação (XP, check-in, conquistas). Dependências injetadas (DIP)."""

    def __init__(
        self,
        sessao: Session,
        kapipass: RepositorioKapiPass | None = None,
        conteudo: ContratoClienteConteudo | None = None,
        autenticacao: ContratoClienteAutenticacao | None = None,
        missoes: RepositorioMissao | None = None,
        diario: RepositorioDiario | None = None,
        criterios_conquista=REGISTRO_CRITERIOS_CONQUISTA,
        estrategias_missao=REGISTRO_ESTRATEGIAS_MISSAO,
        publicador_checkin: PublicadorEventosCheckin | None = None,
    ):
        self.sessao = sessao
        self.kapipass = kapipass or RepositorioKapiPass(sessao)
        self.conteudo = conteudo or ClienteConteudo()
        self.autenticacao = autenticacao or ClienteAutenticacao()
        self.missoes = missoes or RepositorioMissao(sessao)
        self.diario = diario or RepositorioDiario(sessao)
        self._criterios_conquista = criterios_conquista
        self._estrategias_missao = estrategias_missao
        self._publicador_checkin = publicador_checkin or criar_publicador_checkin_padrao()

    def _estatisticas(self, usuario_id: int) -> dict:
        return {
            "visitados": self.kapipass.contar_pontos_visitados(usuario_id),
            "carimbos": self.kapipass.contar_carimbos(usuario_id),
            "conquistas": self.kapipass.contar_conquistas(usuario_id),
        }

    def conceder_xp(self, usuario_id: int, quantidade: int) -> dict:
        registro = self.kapipass.obter_ou_criar_usuario_xp(usuario_id)
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
        stats = self._estatisticas(usuario_id)
        novas: list[dict] = []
        for conquista in self.kapipass.listar_conquistas():
            criterio = self._criterios_conquista.get(conquista.codigo)
            if not criterio:
                continue
            if self.kapipass.tem_conquista(usuario_id, conquista.id):
                continue
            if criterio.atende(stats):
                self.kapipass.conceder_conquista(usuario_id, conquista.id)
                if conquista.xp_bonus:
                    self.conceder_xp(usuario_id, conquista.xp_bonus)
                novas.append(self._serializar_conquista(conquista, desbloqueada=True))
        return novas

    def avaliar_missoes(self, usuario_id: int) -> list[dict]:
        stats = self._estatisticas(usuario_id)
        concluidas: list[dict] = []
        for registro in self.missoes.listar_usuario_missoes(usuario_id):
            if registro.concluida:
                continue
            missao = self.missoes.buscar_missao(registro.missao_id)
            if not missao:
                continue
            estrategia = self._estrategias_missao.get(missao.tipo, ESTRATEGIA_MISSAO_PADRAO)
            progresso = estrategia.calcular_progresso(stats)
            registro.progresso = min(progresso, missao.objetivo_quantidade)
            if registro.progresso >= missao.objetivo_quantidade:
                registro.concluida = True
                registro.data_conclusao = datetime.utcnow()
                self.missoes.salvar(registro)
                if missao.xp:
                    self.conceder_xp(usuario_id, missao.xp)
                concluidas.append({"id": missao.id, "nome": missao.nome, "xp": missao.xp})
            else:
                self.missoes.salvar(registro)
        return concluidas

    def processar_checkin(
        self,
        usuario_id: int,
        ponto_id: int,
        latitude: float | None,
        longitude: float | None,
        raio_m: int = RAIO_PADRAO_CHECKIN_METROS,
    ) -> dict:
        ponto = self.conteudo.buscar_ponto_por_id(ponto_id)
        if not ponto:
            raise ValueError("Ponto turístico não encontrado.")

        distancia = self._validar_distancia_checkin(ponto, latitude, longitude, raio_m)

        xp_inicial = self.kapipass.obter_ou_criar_usuario_xp(usuario_id)
        xp_antes = xp_inicial.xp_total
        nivel_antes = xp_inicial.nivel_atual

        primeira_visita = not self.kapipass.tem_checkin(usuario_id, ponto_id)
        checkin = self.kapipass.criar_checkin(usuario_id, ponto_id, latitude, longitude)

        novo_carimbo = self._conceder_carimbo_se_primeira_visita(usuario_id, ponto_id, primeira_visita)
        efeitos = self._publicador_checkin.publicar(
            ContextoCheckin(
                usuario_id=usuario_id,
                ponto_id=ponto_id,
                ponto=ponto,
                checkin=checkin,
                primeira_visita=primeira_visita,
                gamificacao=self,
            )
        )
        novas_conquistas = efeitos.get("novas_conquistas", [])

        xp_final = self.kapipass.obter_ou_criar_usuario_xp(usuario_id)
        return self._montar_resposta_checkin(
            checkin, ponto, primeira_visita, distancia,
            xp_antes, xp_final, nivel_antes, novo_carimbo, novas_conquistas,
        )

    def _validar_distancia_checkin(
        self, ponto: dict, latitude: float | None, longitude: float | None, raio_m: int
    ) -> float | None:
        if (
            latitude is None
            or longitude is None
            or ponto.get("latitude") is None
            or ponto.get("longitude") is None
        ):
            return None

        distancia = calcular_distancia_haversine_metros(
            latitude, longitude, ponto["latitude"], ponto["longitude"]
        )
        if distancia > raio_m:
            raise ValueError(
                f"Você está muito longe de {ponto['nome']} para fazer check-in "
                f"(aprox. {int(distancia)}m). Aproxime-se do local."
            )
        return distancia

    def _conceder_carimbo_se_primeira_visita(
        self, usuario_id: int, ponto_id: int, primeira_visita: bool
    ) -> dict | None:
        if not primeira_visita:
            return None
        carimbo = self.kapipass.buscar_carimbo_por_ponto(ponto_id)
        if not carimbo or self.kapipass.tem_carimbo(usuario_id, carimbo.id):
            return None
        self.kapipass.conceder_carimbo(usuario_id, carimbo.id)
        self.conceder_xp(usuario_id, carimbo.xp_recompensa or 0)
        return self._serializar_carimbo(carimbo, obtido=True)

    def registrar_diario_primeira_visita(
        self, usuario_id: int, ponto_id: int, ponto: dict, checkin, primeira_visita: bool
    ) -> None:
        if not primeira_visita:
            return
        self.diario.criar(
            usuario_id=usuario_id,
            ponto_turistico_id=ponto_id,
            checkin_id=checkin.id,
            comentario=f"Visitei {ponto['nome']}.",
            foto=ponto.get("url_img"),
        )

    def _montar_resposta_checkin(
        self, checkin, ponto, primeira_visita, distancia,
        xp_antes, xp_final, nivel_antes, novo_carimbo, novas_conquistas,
    ) -> dict:
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

    def obter_passaporte(self, usuario_id: int) -> dict:
        usuario = self.autenticacao.buscar_usuario_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        registro = self.kapipass.obter_ou_criar_usuario_xp(usuario_id)
        nivel = self.kapipass.nivel_para_xp(registro.xp_total)
        proximo = self.kapipass.proximo_nivel(registro.xp_total)

        xp_total = registro.xp_total
        xp_nivel_atual = nivel.xp_minimo if nivel else 0
        xp_proximo = proximo.xp_minimo if proximo else xp_total
        faixa = max(1, xp_proximo - xp_nivel_atual)
        progresso_nivel = min(100, round(((xp_total - xp_nivel_atual) / faixa) * 100)) if proximo else 100

        total_carimbos = len(self.kapipass.listar_carimbos())
        carimbos_obtidos = self.kapipass.contar_carimbos(usuario_id)
        total_conquistas = len(self.kapipass.listar_conquistas())
        conquistas_obtidas = self.kapipass.contar_conquistas(usuario_id)
        visitados = self.kapipass.contar_pontos_visitados(usuario_id)

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
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
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

    def listar_niveis(self) -> list[dict]:
        return [
            {"id": n.id, "nome": n.nome, "xp_minimo": n.xp_minimo, "ordem": n.ordem}
            for n in self.kapipass.listar_niveis()
        ]

    def listar_carimbos(self, usuario_id: int) -> list[dict]:
        obtidos = {uc.carimbo_id: uc for uc in self.kapipass.listar_usuario_carimbos(usuario_id)}
        resultado = []
        for carimbo in self.kapipass.listar_carimbos():
            uc = obtidos.get(carimbo.id)
            data = self._serializar_carimbo(carimbo, obtido=uc is not None)
            data["data_obtencao"] = uc.data_obtencao.isoformat() if uc else None
            resultado.append(data)
        return resultado

    def listar_conquistas(self, usuario_id: int) -> list[dict]:
        obtidas = {uc.conquista_id: uc for uc in self.kapipass.listar_usuario_conquistas(usuario_id)}
        resultado = []
        for conquista in self.kapipass.listar_conquistas():
            uc = obtidas.get(conquista.id)
            data = self._serializar_conquista(conquista, desbloqueada=uc is not None)
            data["data_desbloqueio"] = uc.data_desbloqueio.isoformat() if uc else None
            resultado.append(data)
        return resultado

    def listar_checkins(self, usuario_id: int) -> list[dict]:
        checkins = self.kapipass.listar_checkins(usuario_id)
        ids_pontos = [c.ponto_turistico_id for c in checkins]
        mapa_pontos = {p["id"]: p for p in self.conteudo.buscar_pontos_por_ids(ids_pontos)}
        resultado = []
        for checkin in checkins:
            ponto = mapa_pontos.get(checkin.ponto_turistico_id)
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

    def _serializar_carimbo(self, carimbo, obtido: bool) -> dict:
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

    def _serializar_conquista(self, conquista, desbloqueada: bool) -> dict:
        return {
            "id": conquista.id,
            "codigo": conquista.codigo,
            "nome": conquista.nome,
            "descricao": conquista.descricao,
            "icone": conquista.icone,
            "xp_bonus": conquista.xp_bonus,
            "desbloqueada": desbloqueada,
        }


class ServicoColecao:
    def __init__(
        self,
        sessao: Session | None = None,
        colecoes: RepositorioColecao | None = None,
        kapipass: RepositorioKapiPass | None = None,
        conteudo: ContratoClienteConteudo | None = None,
    ):
        if sessao is None and colecoes is None:
            raise ValueError("Informe sessao ou colecoes.")
        self.colecoes = colecoes or RepositorioColecao(sessao)
        self.kapipass = kapipass or RepositorioKapiPass(sessao)
        self.conteudo = conteudo or ClienteConteudo()

    def listar_colecoes(self, usuario_id: int) -> list[dict]:
        visitados = {c.ponto_turistico_id for c in self.kapipass.listar_checkins(usuario_id)}
        resultado = []
        for colecao in self.colecoes.listar_colecoes():
            ids_pontos = self.colecoes.listar_pontos_da_colecao(colecao.id)
            total = len(ids_pontos)
            concluidos = sum(1 for pid in ids_pontos if pid in visitados)
            percentual = round((concluidos / total) * 100) if total else 0
            pontos = [
                {
                    "id": ponto["id"],
                    "nome": ponto["nome"],
                    "url_img": ponto.get("url_img"),
                    "visitado": ponto["id"] in visitados,
                }
                for ponto in self.conteudo.buscar_pontos_por_ids(ids_pontos)
            ]
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


class ServicoMissao:
    def __init__(
        self,
        sessao: Session | None = None,
        missoes: RepositorioMissao | None = None,
        gamificacao: ServicoGamificacao | None = None,
    ):
        if sessao is None and missoes is None:
            raise ValueError("Informe sessao ou missoes.")
        self.missoes = missoes or RepositorioMissao(sessao)
        self.gamificacao = gamificacao or ServicoGamificacao(sessao)

    def listar_missoes(self, usuario_id: int) -> list[dict]:
        self.gamificacao.avaliar_missoes(usuario_id)
        aceitas = {m.missao_id: m for m in self.missoes.listar_usuario_missoes(usuario_id)}
        resultado = []
        for missao in self.missoes.listar_ativas():
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
        missao = self.missoes.buscar_missao(missao_id)
        if not missao or not missao.ativo:
            raise ValueError("Missão não encontrada ou inativa.")
        if self.missoes.buscar_usuario_missao(usuario_id, missao_id):
            raise ValueError("Você já aceitou esta missão.")
        self.missoes.aceitar(usuario_id, missao_id)
        self.gamificacao.avaliar_missoes(usuario_id)
        return {"success": True, "message": "Missão aceita!"}


class ServicoEco:
    def __init__(
        self,
        sessao: Session | None = None,
        eco: RepositorioEco | None = None,
        gamificacao: ServicoGamificacao | None = None,
    ):
        if sessao is None and eco is None:
            raise ValueError("Informe sessao ou eco.")
        self.eco = eco or RepositorioEco(sessao)
        self.gamificacao = gamificacao or ServicoGamificacao(sessao)

    def listar_atividades(self, usuario_id: int) -> dict:
        registradas = {}
        for r in self.eco.listar_usuario_atividades(usuario_id):
            registradas[r.eco_atividade_id] = registradas.get(r.eco_atividade_id, 0) + 1
        atividades = [
            {
                "id": atividade.id,
                "nome": atividade.nome,
                "descricao": atividade.descricao,
                "tipo": atividade.tipo,
                "pontuacao_eco": atividade.pontuacao_eco,
                "xp_recompensa": atividade.xp_recompensa,
                "vezes_registrada": registradas.get(atividade.id, 0),
            }
            for atividade in self.eco.listar_atividades()
        ]
        return {
            "pontuacao_eco_total": self.eco.pontuacao_total(usuario_id),
            "atividades": atividades,
        }

    def registrar(self, usuario_id: int, atividade_id: int) -> dict:
        atividade = self.eco.buscar_atividade(atividade_id)
        if not atividade:
            raise ValueError("Atividade ecológica não encontrada.")
        self.eco.registrar(usuario_id, atividade_id, atividade.pontuacao_eco or 0)
        if atividade.xp_recompensa:
            self.gamificacao.conceder_xp(usuario_id, atividade.xp_recompensa)
        return {
            "success": True,
            "message": f"Atividade registrada! +{atividade.pontuacao_eco} EcoPontos.",
            "pontuacao_eco_total": self.eco.pontuacao_total(usuario_id),
        }


class ServicoDiario:
    def __init__(
        self,
        sessao: Session | None = None,
        diario: RepositorioDiario | None = None,
        conteudo: ContratoClienteConteudo | None = None,
    ):
        if sessao is None and diario is None:
            raise ValueError("Informe sessao ou diario.")
        self.diario = diario or RepositorioDiario(sessao)
        self.conteudo = conteudo or ClienteConteudo()

    def listar_entradas(self, usuario_id: int) -> list[dict]:
        entradas = self.diario.listar_por_usuario(usuario_id)
        ids_pontos = [e.ponto_turistico_id for e in entradas if e.ponto_turistico_id]
        mapa_pontos = {p["id"]: p for p in self.conteudo.buscar_pontos_por_ids(ids_pontos)}
        resultado = []
        for entrada in entradas:
            ponto = mapa_pontos.get(entrada.ponto_turistico_id) if entrada.ponto_turistico_id else None
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
        entrada = self.diario.criar(usuario_id, ponto_turistico_id, checkin_id, comentario, foto)
        return {
            "id": entrada.id,
            "usuario_id": entrada.usuario_id,
            "ponto_turistico_id": entrada.ponto_turistico_id,
            "checkin_id": entrada.checkin_id,
            "comentario": entrada.comentario,
            "foto": entrada.foto,
            "data": entrada.data.isoformat(),
        }


class ServicoTesouro:
    def __init__(
        self,
        sessao: Session | None = None,
        tesouros: RepositorioTesouro | None = None,
        kapipass: RepositorioKapiPass | None = None,
        gamificacao: ServicoGamificacao | None = None,
    ):
        if sessao is None and tesouros is None:
            raise ValueError("Informe sessao ou tesouros.")
        self.tesouros = tesouros or RepositorioTesouro(sessao)
        self.kapipass = kapipass or RepositorioKapiPass(sessao)
        self.gamificacao = gamificacao or ServicoGamificacao(sessao)

    def listar_tesouros(self, usuario_id: int) -> list[dict]:
        concluidos = {t.tesouro_id for t in self.tesouros.listar_usuario_tesouros(usuario_id)}
        resultado = []
        for tesouro in self.tesouros.listar_tesouros():
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
        tesouro = self.tesouros.buscar_tesouro(tesouro_id)
        if not tesouro:
            raise ValueError("Tesouro não encontrado.")
        if self.tesouros.ja_concluido(usuario_id, tesouro_id):
            raise ValueError("Você já concluiu este tesouro.")
        self.tesouros.concluir(usuario_id, tesouro_id)

        recompensas = self._aplicar_recompensas_tesouro(usuario_id, tesouro)
        return {
            "success": True,
            "message": "Tesouro encontrado!",
            "recompensas": recompensas,
        }

    def _aplicar_recompensas_tesouro(self, usuario_id: int, tesouro) -> list[str]:
        recompensas = []
        if tesouro.carimbo_id and not self.kapipass.tem_carimbo(usuario_id, tesouro.carimbo_id):
            self.kapipass.conceder_carimbo(usuario_id, tesouro.carimbo_id)
            recompensas.append("carimbo especial")
        if tesouro.conquista_id and not self.kapipass.tem_conquista(usuario_id, tesouro.conquista_id):
            self.kapipass.conceder_conquista(usuario_id, tesouro.conquista_id)
            recompensas.append("conquista especial")
        if tesouro.xp_bonus:
            self.gamificacao.conceder_xp(usuario_id, tesouro.xp_bonus)
            recompensas.append(f"+{tesouro.xp_bonus} XP")
        return recompensas


class ServicoRanking:
    CATEGORIAS = set(REGISTRO_ESTRATEGIAS_RANKING.keys())

    def __init__(
        self,
        sessao: Session | None = None,
        rankings: RepositorioRanking | None = None,
        autenticacao: ContratoClienteAutenticacao | None = None,
        estrategias=REGISTRO_ESTRATEGIAS_RANKING,
    ):
        if sessao is None and rankings is None:
            raise ValueError("Informe sessao ou rankings.")
        self.rankings = rankings or RepositorioRanking(sessao)
        self.autenticacao = autenticacao or ClienteAutenticacao()
        self._estrategias = estrategias

    def obter_ranking(self, categoria: str, pagina: int = 1, tamanho: int = 20) -> dict:
        categoria = (categoria or "exploradores").lower()
        pagina = max(1, pagina)
        tamanho = max(1, min(tamanho, 100))

        linhas, unidade = self._buscar_linhas_ranking(categoria, pagina, tamanho)
        ids_usuarios = [int(linha[0]) for linha in linhas]
        mapa_usuarios = self.autenticacao.buscar_usuarios_em_lote(ids_usuarios)
        inicio = (pagina - 1) * tamanho
        itens = []
        for i, linha in enumerate(linhas):
            usuario_id = int(linha[0])
            usuario = mapa_usuarios.get(usuario_id)
            itens.append(
                {
                    "posicao": inicio + i + 1,
                    "usuario_id": usuario_id,
                    "nome": usuario["nome"] if usuario else f"Usuário {usuario_id}",
                    "valor": int(linha[1] if categoria == "xp" else linha[1]),
                    "unidade": unidade,
                }
            )
        return {"categoria": categoria, "page": pagina, "size": tamanho, "pagina": pagina, "tamanho": tamanho, "itens": itens}

    def _buscar_linhas_ranking(self, categoria: str, pagina: int, tamanho: int) -> tuple:
        estrategia = self._estrategias.get(categoria, self._estrategias["exploradores"])
        return estrategia.buscar_linhas(self.rankings, pagina, tamanho), estrategia.unidade
