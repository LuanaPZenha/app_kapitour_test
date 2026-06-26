from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
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


class KapiPassRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_niveis(self) -> list[KapiPassNivel]:
        return self.db.query(KapiPassNivel).order_by(KapiPassNivel.xp_minimo).all()

    def nivel_para_xp(self, xp: int) -> KapiPassNivel | None:
        return (
            self.db.query(KapiPassNivel)
            .filter(KapiPassNivel.xp_minimo <= xp)
            .order_by(KapiPassNivel.xp_minimo.desc())
            .first()
        )

    def proximo_nivel(self, xp: int) -> KapiPassNivel | None:
        return (
            self.db.query(KapiPassNivel)
            .filter(KapiPassNivel.xp_minimo > xp)
            .order_by(KapiPassNivel.xp_minimo)
            .first()
        )

    def get_usuario_xp(self, usuario_id: int) -> UsuarioXp | None:
        return self.db.query(UsuarioXp).filter(UsuarioXp.usuario_id == usuario_id).first()

    def get_or_create_usuario_xp(self, usuario_id: int) -> UsuarioXp:
        registro = self.get_usuario_xp(usuario_id)
        if registro:
            return registro
        registro = UsuarioXp(usuario_id=usuario_id, xp_total=0, nivel_atual=1)
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def salvar_usuario_xp(self, registro: UsuarioXp) -> UsuarioXp:
        registro.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def list_carimbos(self) -> list[KapiPassCarimbo]:
        return self.db.query(KapiPassCarimbo).all()

    def get_carimbo_por_ponto(self, ponto_id: int) -> KapiPassCarimbo | None:
        return (
            self.db.query(KapiPassCarimbo)
            .filter(KapiPassCarimbo.ponto_turistico_id == ponto_id)
            .first()
        )

    def list_usuario_carimbos(self, usuario_id: int) -> list[UsuarioCarimbo]:
        return self.db.query(UsuarioCarimbo).filter(UsuarioCarimbo.usuario_id == usuario_id).all()

    def tem_carimbo(self, usuario_id: int, carimbo_id: int) -> bool:
        return (
            self.db.query(UsuarioCarimbo)
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
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def count_carimbos(self, usuario_id: int) -> int:
        return self.db.query(UsuarioCarimbo).filter(UsuarioCarimbo.usuario_id == usuario_id).count()

    def list_checkins(self, usuario_id: int) -> list[Checkin]:
        return (
            self.db.query(Checkin)
            .filter(Checkin.usuario_id == usuario_id)
            .order_by(Checkin.data_checkin.desc())
            .all()
        )

    def tem_checkin(self, usuario_id: int, ponto_id: int) -> bool:
        return (
            self.db.query(Checkin)
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
        self.db.add(checkin)
        self.db.commit()
        self.db.refresh(checkin)
        return checkin

    def count_pontos_visitados(self, usuario_id: int) -> int:
        return (
            self.db.query(Checkin.ponto_turistico_id)
            .filter(Checkin.usuario_id == usuario_id)
            .distinct()
            .count()
        )

    def list_conquistas(self) -> list[Conquista]:
        return self.db.query(Conquista).all()

    def list_usuario_conquistas(self, usuario_id: int) -> list[UsuarioConquista]:
        return (
            self.db.query(UsuarioConquista)
            .filter(UsuarioConquista.usuario_id == usuario_id)
            .all()
        )

    def tem_conquista(self, usuario_id: int, conquista_id: int) -> bool:
        return (
            self.db.query(UsuarioConquista)
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
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def count_conquistas(self, usuario_id: int) -> int:
        return (
            self.db.query(UsuarioConquista)
            .filter(UsuarioConquista.usuario_id == usuario_id)
            .count()
        )


class CollectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_colecoes(self) -> list[Colecao]:
        return self.db.query(Colecao).order_by(Colecao.id).all()

    def list_pontos_da_colecao(self, colecao_id: int) -> list[int]:
        return [
            row.ponto_turistico_id
            for row in self.db.query(ColecaoPonto)
            .filter(ColecaoPonto.colecao_id == colecao_id)
            .all()
        ]


class MissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_ativas(self) -> list[Missao]:
        return self.db.query(Missao).filter(Missao.ativo.is_(True)).order_by(Missao.id).all()

    def get_missao(self, missao_id: int) -> Missao | None:
        return self.db.query(Missao).filter(Missao.id == missao_id).first()

    def get_usuario_missao(self, usuario_id: int, missao_id: int) -> UsuarioMissao | None:
        return (
            self.db.query(UsuarioMissao)
            .filter(UsuarioMissao.usuario_id == usuario_id, UsuarioMissao.missao_id == missao_id)
            .first()
        )

    def list_usuario_missoes(self, usuario_id: int) -> list[UsuarioMissao]:
        return self.db.query(UsuarioMissao).filter(UsuarioMissao.usuario_id == usuario_id).all()

    def aceitar(self, usuario_id: int, missao_id: int) -> UsuarioMissao:
        registro = UsuarioMissao(
            usuario_id=usuario_id,
            missao_id=missao_id,
            progresso=0,
            concluida=False,
            data_inicio=datetime.utcnow(),
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def salvar(self, registro: UsuarioMissao) -> UsuarioMissao:
        self.db.commit()
        self.db.refresh(registro)
        return registro


class EcoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_atividades(self) -> list[EcoAtividade]:
        return self.db.query(EcoAtividade).order_by(EcoAtividade.id).all()

    def get_atividade(self, atividade_id: int) -> EcoAtividade | None:
        return self.db.query(EcoAtividade).filter(EcoAtividade.id == atividade_id).first()

    def list_usuario_atividades(self, usuario_id: int) -> list[UsuarioEcoAtividade]:
        return (
            self.db.query(UsuarioEcoAtividade)
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
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def pontuacao_total(self, usuario_id: int) -> int:
        total = (
            self.db.query(func.coalesce(func.sum(UsuarioEcoAtividade.pontuacao), 0))
            .filter(UsuarioEcoAtividade.usuario_id == usuario_id)
            .scalar()
        )
        return int(total or 0)


class DiaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, usuario_id: int) -> list[DiarioViagem]:
        return (
            self.db.query(DiarioViagem)
            .filter(DiarioViagem.usuario_id == usuario_id)
            .order_by(DiarioViagem.data.desc())
            .all()
        )

    def create(
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
        self.db.add(entrada)
        self.db.commit()
        self.db.refresh(entrada)
        return entrada


class TreasureRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_tesouros(self) -> list[Tesouro]:
        return self.db.query(Tesouro).order_by(Tesouro.id).all()

    def get_tesouro(self, tesouro_id: int) -> Tesouro | None:
        return self.db.query(Tesouro).filter(Tesouro.id == tesouro_id).first()

    def list_usuario_tesouros(self, usuario_id: int) -> list[UsuarioTesouro]:
        return self.db.query(UsuarioTesouro).filter(UsuarioTesouro.usuario_id == usuario_id).all()

    def ja_concluido(self, usuario_id: int, tesouro_id: int) -> bool:
        return (
            self.db.query(UsuarioTesouro)
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
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro


class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def _paginar(self, query, page: int, size: int):
        return query.limit(size).offset((page - 1) * size).all()

    def ranking_xp(self, page: int, size: int) -> list[tuple]:
        query = self.db.query(UsuarioXp.usuario_id, UsuarioXp.xp_total).order_by(
            UsuarioXp.xp_total.desc()
        )
        return self._paginar(query, page, size)

    def ranking_carimbos(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                UsuarioCarimbo.usuario_id,
                func.count(UsuarioCarimbo.id).label("total"),
            )
            .group_by(UsuarioCarimbo.usuario_id)
            .order_by(func.count(UsuarioCarimbo.id).desc())
        )
        return self._paginar(query, page, size)

    def ranking_checkins(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                Checkin.usuario_id,
                func.count(func.distinct(Checkin.ponto_turistico_id)).label("total"),
            )
            .group_by(Checkin.usuario_id)
            .order_by(func.count(func.distinct(Checkin.ponto_turistico_id)).desc())
        )
        return self._paginar(query, page, size)

    def ranking_eco(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                UsuarioEcoAtividade.usuario_id,
                func.coalesce(func.sum(UsuarioEcoAtividade.pontuacao), 0).label("total"),
            )
            .group_by(UsuarioEcoAtividade.usuario_id)
            .order_by(func.sum(UsuarioEcoAtividade.pontuacao).desc())
        )
        return self._paginar(query, page, size)
