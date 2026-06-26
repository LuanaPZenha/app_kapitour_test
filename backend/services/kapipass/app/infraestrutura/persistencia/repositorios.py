from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.infraestrutura.persistencia.modelos import (
    Checkin,
    Colecao,
    ColecaoPonto,
    Conquista,
    DiarioViagem,
    EcoAtividade,
    KapiPassCarimbo,
    KapiPassNivel,
    Missao,
    Tesouro,
    UsuarioCarimbo,
    UsuarioConquista,
    UsuarioEcoAtividade,
    UsuarioMissao,
    UsuarioTesouro,
    UsuarioXp,
)


class RepositorioKapiPass:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_niveis(self) -> list[KapiPassNivel]:
        return self.sessao.query(KapiPassNivel).order_by(KapiPassNivel.xp_minimo).all()

    def nivel_para_xp(self, xp: int) -> KapiPassNivel | None:
        return (
            self.sessao.query(KapiPassNivel)
            .filter(KapiPassNivel.xp_minimo <= xp)
            .order_by(KapiPassNivel.xp_minimo.desc())
            .first()
        )

    def proximo_nivel(self, xp: int) -> KapiPassNivel | None:
        return (
            self.sessao.query(KapiPassNivel)
            .filter(KapiPassNivel.xp_minimo > xp)
            .order_by(KapiPassNivel.xp_minimo)
            .first()
        )

    def buscar_usuario_xp(self, usuario_id: int) -> UsuarioXp | None:
        return self.sessao.query(UsuarioXp).filter(UsuarioXp.usuario_id == usuario_id).first()

    def obter_ou_criar_usuario_xp(self, usuario_id: int) -> UsuarioXp:
        registro = self.buscar_usuario_xp(usuario_id)
        if registro:
            return registro
        registro = UsuarioXp(usuario_id=usuario_id, xp_total=0, nivel_atual=1)
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def salvar_usuario_xp(self, registro: UsuarioXp) -> UsuarioXp:
        registro.atualizado_em = datetime.utcnow()
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def listar_carimbos(self) -> list[KapiPassCarimbo]:
        return self.sessao.query(KapiPassCarimbo).all()

    def buscar_carimbo_por_ponto(self, ponto_id: int) -> KapiPassCarimbo | None:
        return (
            self.sessao.query(KapiPassCarimbo)
            .filter(KapiPassCarimbo.ponto_turistico_id == ponto_id)
            .first()
        )

    def listar_usuario_carimbos(self, usuario_id: int) -> list[UsuarioCarimbo]:
        return (
            self.sessao.query(UsuarioCarimbo)
            .filter(UsuarioCarimbo.usuario_id == usuario_id)
            .all()
        )

    def tem_carimbo(self, usuario_id: int, carimbo_id: int) -> bool:
        return (
            self.sessao.query(UsuarioCarimbo)
            .filter(
                UsuarioCarimbo.usuario_id == usuario_id,
                UsuarioCarimbo.carimbo_id == carimbo_id,
            )
            .first()
            is not None
        )

    def conceder_carimbo(self, usuario_id: int, carimbo_id: int) -> UsuarioCarimbo:
        registro = UsuarioCarimbo(
            usuario_id=usuario_id,
            carimbo_id=carimbo_id,
            data_obtencao=datetime.utcnow(),
        )
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def contar_carimbos(self, usuario_id: int) -> int:
        return (
            self.sessao.query(UsuarioCarimbo)
            .filter(UsuarioCarimbo.usuario_id == usuario_id)
            .count()
        )

    def listar_checkins(self, usuario_id: int) -> list[Checkin]:
        return (
            self.sessao.query(Checkin)
            .filter(Checkin.usuario_id == usuario_id)
            .order_by(Checkin.data_checkin.desc())
            .all()
        )

    def tem_checkin(self, usuario_id: int, ponto_id: int) -> bool:
        return (
            self.sessao.query(Checkin)
            .filter(
                Checkin.usuario_id == usuario_id,
                Checkin.ponto_turistico_id == ponto_id,
            )
            .first()
            is not None
        )

    def criar_checkin(
        self, usuario_id: int, ponto_id: int, latitude: float | None, longitude: float | None
    ) -> Checkin:
        checkin = Checkin(
            usuario_id=usuario_id,
            ponto_turistico_id=ponto_id,
            data_checkin=datetime.utcnow(),
            latitude=latitude,
            longitude=longitude,
        )
        self.sessao.add(checkin)
        self.sessao.commit()
        self.sessao.refresh(checkin)
        return checkin

    def contar_pontos_visitados(self, usuario_id: int) -> int:
        return (
            self.sessao.query(Checkin.ponto_turistico_id)
            .filter(Checkin.usuario_id == usuario_id)
            .distinct()
            .count()
        )

    def listar_conquistas(self) -> list[Conquista]:
        return self.sessao.query(Conquista).all()

    def listar_usuario_conquistas(self, usuario_id: int) -> list[UsuarioConquista]:
        return (
            self.sessao.query(UsuarioConquista)
            .filter(UsuarioConquista.usuario_id == usuario_id)
            .all()
        )

    def tem_conquista(self, usuario_id: int, conquista_id: int) -> bool:
        return (
            self.sessao.query(UsuarioConquista)
            .filter(
                UsuarioConquista.usuario_id == usuario_id,
                UsuarioConquista.conquista_id == conquista_id,
            )
            .first()
            is not None
        )

    def conceder_conquista(self, usuario_id: int, conquista_id: int) -> UsuarioConquista:
        registro = UsuarioConquista(
            usuario_id=usuario_id,
            conquista_id=conquista_id,
            data_desbloqueio=datetime.utcnow(),
        )
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def contar_conquistas(self, usuario_id: int) -> int:
        return (
            self.sessao.query(UsuarioConquista)
            .filter(UsuarioConquista.usuario_id == usuario_id)
            .count()
        )


class RepositorioColecao:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_colecoes(self) -> list[Colecao]:
        return self.sessao.query(Colecao).order_by(Colecao.id).all()

    def listar_pontos_da_colecao(self, colecao_id: int) -> list[int]:
        return [
            linha.ponto_turistico_id
            for linha in self.sessao.query(ColecaoPonto)
            .filter(ColecaoPonto.colecao_id == colecao_id)
            .all()
        ]


class RepositorioMissao:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_ativas(self) -> list[Missao]:
        return (
            self.sessao.query(Missao)
            .filter(Missao.ativo.is_(True))
            .order_by(Missao.id)
            .all()
        )

    def buscar_missao(self, missao_id: int) -> Missao | None:
        return self.sessao.query(Missao).filter(Missao.id == missao_id).first()

    def buscar_usuario_missao(self, usuario_id: int, missao_id: int) -> UsuarioMissao | None:
        return (
            self.sessao.query(UsuarioMissao)
            .filter(UsuarioMissao.usuario_id == usuario_id, UsuarioMissao.missao_id == missao_id)
            .first()
        )

    def listar_usuario_missoes(self, usuario_id: int) -> list[UsuarioMissao]:
        return (
            self.sessao.query(UsuarioMissao)
            .filter(UsuarioMissao.usuario_id == usuario_id)
            .all()
        )

    def aceitar(self, usuario_id: int, missao_id: int) -> UsuarioMissao:
        registro = UsuarioMissao(
            usuario_id=usuario_id,
            missao_id=missao_id,
            progresso=0,
            concluida=False,
            data_inicio=datetime.utcnow(),
        )
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def salvar(self, registro: UsuarioMissao) -> UsuarioMissao:
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro


class RepositorioEco:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_atividades(self) -> list[EcoAtividade]:
        return self.sessao.query(EcoAtividade).order_by(EcoAtividade.id).all()

    def buscar_atividade(self, atividade_id: int) -> EcoAtividade | None:
        return self.sessao.query(EcoAtividade).filter(EcoAtividade.id == atividade_id).first()

    def listar_usuario_atividades(self, usuario_id: int) -> list[UsuarioEcoAtividade]:
        return (
            self.sessao.query(UsuarioEcoAtividade)
            .filter(UsuarioEcoAtividade.usuario_id == usuario_id)
            .order_by(UsuarioEcoAtividade.data.desc())
            .all()
        )

    def registrar(self, usuario_id: int, atividade_id: int, pontuacao: int) -> UsuarioEcoAtividade:
        registro = UsuarioEcoAtividade(
            usuario_id=usuario_id,
            eco_atividade_id=atividade_id,
            data=datetime.utcnow(),
            pontuacao=pontuacao,
        )
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro

    def pontuacao_total(self, usuario_id: int) -> int:
        total = (
            self.sessao.query(func.coalesce(func.sum(UsuarioEcoAtividade.pontuacao), 0))
            .filter(UsuarioEcoAtividade.usuario_id == usuario_id)
            .scalar()
        )
        return int(total or 0)


class RepositorioDiario:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_por_usuario(self, usuario_id: int) -> list[DiarioViagem]:
        return (
            self.sessao.query(DiarioViagem)
            .filter(DiarioViagem.usuario_id == usuario_id)
            .order_by(DiarioViagem.data.desc())
            .all()
        )

    def criar(
        self,
        usuario_id: int,
        ponto_turistico_id: int | None,
        checkin_id: int | None,
        comentario: str | None,
        foto: str | None,
    ) -> DiarioViagem:
        entrada = DiarioViagem(
            usuario_id=usuario_id,
            ponto_turistico_id=ponto_turistico_id,
            checkin_id=checkin_id,
            comentario=comentario,
            foto=foto,
            data=datetime.utcnow(),
        )
        self.sessao.add(entrada)
        self.sessao.commit()
        self.sessao.refresh(entrada)
        return entrada


class RepositorioTesouro:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_tesouros(self) -> list[Tesouro]:
        return self.sessao.query(Tesouro).order_by(Tesouro.id).all()

    def buscar_tesouro(self, tesouro_id: int) -> Tesouro | None:
        return self.sessao.query(Tesouro).filter(Tesouro.id == tesouro_id).first()

    def listar_usuario_tesouros(self, usuario_id: int) -> list[UsuarioTesouro]:
        return (
            self.sessao.query(UsuarioTesouro)
            .filter(UsuarioTesouro.usuario_id == usuario_id)
            .all()
        )

    def ja_concluido(self, usuario_id: int, tesouro_id: int) -> bool:
        return (
            self.sessao.query(UsuarioTesouro)
            .filter(
                UsuarioTesouro.usuario_id == usuario_id,
                UsuarioTesouro.tesouro_id == tesouro_id,
            )
            .first()
            is not None
        )

    def concluir(self, usuario_id: int, tesouro_id: int) -> UsuarioTesouro:
        registro = UsuarioTesouro(
            usuario_id=usuario_id,
            tesouro_id=tesouro_id,
            data_conclusao=datetime.utcnow(),
        )
        self.sessao.add(registro)
        self.sessao.commit()
        self.sessao.refresh(registro)
        return registro


class RepositorioRanking:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def _paginar(self, consulta, pagina: int, tamanho: int):
        return consulta.limit(tamanho).offset((pagina - 1) * tamanho).all()

    def ranking_xp(self, pagina: int, tamanho: int) -> list[tuple]:
        consulta = self.sessao.query(UsuarioXp.usuario_id, UsuarioXp.xp_total).order_by(
            UsuarioXp.xp_total.desc()
        )
        return self._paginar(consulta, pagina, tamanho)

    def ranking_carimbos(self, pagina: int, tamanho: int) -> list[tuple]:
        consulta = (
            self.sessao.query(
                UsuarioCarimbo.usuario_id,
                func.count(UsuarioCarimbo.id).label("total"),
            )
            .group_by(UsuarioCarimbo.usuario_id)
            .order_by(func.count(UsuarioCarimbo.id).desc())
        )
        return self._paginar(consulta, pagina, tamanho)

    def ranking_checkins(self, pagina: int, tamanho: int) -> list[tuple]:
        consulta = (
            self.sessao.query(
                Checkin.usuario_id,
                func.count(func.distinct(Checkin.ponto_turistico_id)).label("total"),
            )
            .group_by(Checkin.usuario_id)
            .order_by(func.count(func.distinct(Checkin.ponto_turistico_id)).desc())
        )
        return self._paginar(consulta, pagina, tamanho)

    def ranking_eco(self, pagina: int, tamanho: int) -> list[tuple]:
        consulta = (
            self.sessao.query(
                UsuarioEcoAtividade.usuario_id,
                func.coalesce(func.sum(UsuarioEcoAtividade.pontuacao), 0).label("total"),
            )
            .group_by(UsuarioEcoAtividade.usuario_id)
            .order_by(func.sum(UsuarioEcoAtividade.pontuacao).desc())
        )
        return self._paginar(consulta, pagina, tamanho)
