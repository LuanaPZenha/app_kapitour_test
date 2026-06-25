from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models import (
    Avaliacao,
    Campanha,
    Categoria,
    Checkin,
    Colecao,
    ColecaoPonto,
    Conquista,
    Cupom,
    CupomResgatado,
    DiarioViagem,
    EcoAtividade,
    Estoque,
    Favorito,
    KapiPassCarimbo,
    KapiPassNivel,
    Missao,
    PontoAvaliacao,
    PontoCategoria,
    PontoTuristico,
    Produto,
    Rota,
    RotaPonto,
    Tesouro,
    TipoProduto,
    Usuario,
    UsuarioCarimbo,
    UsuarioConquista,
    UsuarioEcoAtividade,
    UsuarioMissao,
    UsuarioTesouro,
    UsuarioXp,
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_auth_id(self, auth_id: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.auth_id == auth_id).first()

    def get_by_id(self, user_id: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email.lower()).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, nome: str, email: str, password: str, **kwargs) -> Usuario:
        user = Usuario(
            auth_id=str(uuid4()),
            nome=nome,
            email=email.lower(),
            senha_hash=hash_password(password),
            data_criacao=datetime.utcnow(),
            **kwargs,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: Usuario, data: dict) -> Usuario:
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Usuario | None:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.senha_hash):
            return None
        return user


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Categoria]:
        return self.db.query(Categoria).order_by(Categoria.nome).all()


class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, categoria_id: int | None = None) -> list[PontoTuristico]:
        query = self.db.query(PontoTuristico)
        if categoria_id:
            ponto_ids = [
                row.ponto_id
                for row in self.db.query(PontoCategoria)
                .filter(PontoCategoria.categoria_id == categoria_id)
                .all()
            ]
            if not ponto_ids:
                return []
            query = query.filter(PontoTuristico.id.in_(ponto_ids))
        return query.all()

    def get_by_ids(self, ids: list[int]) -> list[PontoTuristico]:
        if not ids:
            return []
        return self.db.query(PontoTuristico).filter(PontoTuristico.id.in_(ids)).all()

    def get_by_id(self, place_id: int) -> PontoTuristico | None:
        return self.db.query(PontoTuristico).filter(PontoTuristico.id == place_id).first()

    def get_ponto_categorias(self, ponto_ids: list[int]) -> list[PontoCategoria]:
        if not ponto_ids:
            return []
        return self.db.query(PontoCategoria).filter(PontoCategoria.ponto_id.in_(ponto_ids)).all()


class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Rota]:
        return self.db.query(Rota).order_by(Rota.id).all()

    def get_rota_pontos(self, rota_id: int) -> list[RotaPonto]:
        return (
            self.db.query(RotaPonto)
            .filter(RotaPonto.rota_id == rota_id)
            .order_by(RotaPonto.ordem)
            .all()
        )

    def get_rota_pontos_by_ponto_ids(self, ponto_ids: list[int]) -> list[RotaPonto]:
        if not ponto_ids:
            return []
        return self.db.query(RotaPonto).filter(RotaPonto.ponto_id.in_(ponto_ids)).all()

    def get_rotas_by_ids(self, ids: list[int]) -> list[Rota]:
        if not ids:
            return []
        return self.db.query(Rota).filter(Rota.id.in_(ids)).all()


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, usuario_id: int) -> list[Favorito]:
        return self.db.query(Favorito).filter(Favorito.usuario_id == usuario_id).all()

    def get(self, usuario_id: int, ponto_id: int) -> Favorito | None:
        return (
            self.db.query(Favorito)
            .filter(Favorito.usuario_id == usuario_id, Favorito.ponto_id == ponto_id)
            .first()
        )

    def create(self, usuario_id: int, ponto_id: int) -> Favorito:
        favorito = Favorito(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            data_adicionado=datetime.utcnow(),
        )
        self.db.add(favorito)
        self.db.commit()
        self.db.refresh(favorito)
        return favorito

    def delete(self, usuario_id: int, ponto_id: int) -> bool:
        favorito = self.get(usuario_id, ponto_id)
        if not favorito:
            return False
        self.db.delete(favorito)
        self.db.commit()
        return True


class RatingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_ponto(self, ponto_id: int) -> list[Avaliacao]:
        return self.db.query(Avaliacao).filter(Avaliacao.ponto_id == ponto_id).all()

    def get_user_rating(self, usuario_id: int, ponto_id: int) -> Avaliacao | None:
        return (
            self.db.query(Avaliacao)
            .filter(Avaliacao.usuario_id == usuario_id, Avaliacao.ponto_id == ponto_id)
            .first()
        )

    def create(self, usuario_id: int, ponto_id: int, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao = Avaliacao(
            usuario_id=usuario_id,
            ponto_id=ponto_id,
            nota=nota,
            comentario=comentario,
            data_avaliacao=datetime.utcnow(),
        )
        self.db.add(avaliacao)
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    def update(self, avaliacao: Avaliacao, nota: int, comentario: str | None) -> Avaliacao:
        avaliacao.nota = nota
        avaliacao.comentario = comentario
        avaliacao.data_avaliacao = datetime.utcnow()
        self.db.commit()
        self.db.refresh(avaliacao)
        return avaliacao

    def create_ponto_avaliacao(
        self, ponto_id: int, usuario_id: int | None, nota: int, comentario: str | None
    ) -> PontoAvaliacao:
        item = PontoAvaliacao(
            ponto_id=ponto_id,
            usuario_id=usuario_id,
            nota=nota,
            comentario=comentario,
            data=datetime.utcnow(),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_ponto_avaliacoes(self, ponto_id: int) -> list[PontoAvaliacao]:
        return self.db.query(PontoAvaliacao).filter(PontoAvaliacao.ponto_id == ponto_id).all()


class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_produtos(self) -> list[Produto]:
        return self.db.query(Produto).all()

    def list_tipos(self) -> list[TipoProduto]:
        return self.db.query(TipoProduto).all()

    def list_estoque(self) -> list[Estoque]:
        return self.db.query(Estoque).all()


class CouponRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_available(self, parceiro_id: int | None = None) -> list[Cupom]:
        query = self.db.query(Cupom).filter(Cupom.quantidade_disponivel > 0)
        if parceiro_id:
            query = query.filter(Cupom.parceiro_id == parceiro_id)
        return query.all()

    def get_by_id(self, cupom_id: int) -> Cupom | None:
        return self.db.query(Cupom).filter(Cupom.id == cupom_id).first()

    def get_campanha(self, campanha_id: int) -> Campanha | None:
        return self.db.query(Campanha).filter(Campanha.id == campanha_id).first()

    def list_resgatados(self, usuario_id: int) -> list[CupomResgatado]:
        return self.db.query(CupomResgatado).filter(CupomResgatado.usuario_id == usuario_id).all()

    def already_redeemed(self, cupom_id: int, usuario_id: int) -> bool:
        return (
            self.db.query(CupomResgatado)
            .filter(
                CupomResgatado.cupom_id == cupom_id,
                CupomResgatado.usuario_id == usuario_id,
            )
            .first()
            is not None
        )

    def redeem(self, cupom: Cupom, usuario_id: int) -> CupomResgatado:
        resgate = CupomResgatado(
            cupom_id=cupom.id,
            usuario_id=usuario_id,
            data_resgate=datetime.utcnow(),
        )
        cupom.quantidade_disponivel -= 1
        self.db.add(resgate)
        self.db.commit()
        self.db.refresh(resgate)
        return resgate

    def list_by_parceiro(self, parceiro_id: int) -> list[Cupom]:
        return self.db.query(Cupom).filter(Cupom.parceiro_id == parceiro_id).all()


class KapiPassRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Níveis ──
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

    # ── XP do usuário ──
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

    # ── Carimbos ──
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

    # ── Check-ins ──
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

    # ── Conquistas ──
    def list_conquistas(self) -> list[Conquista]:
        return self.db.query(Conquista).all()

    def get_conquista_por_codigo(self, codigo: str) -> Conquista | None:
        return self.db.query(Conquista).filter(Conquista.codigo == codigo).first()

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
        query = (
            self.db.query(Usuario.id, Usuario.nome, UsuarioXp.xp_total)
            .join(UsuarioXp, UsuarioXp.usuario_id == Usuario.id)
            .order_by(UsuarioXp.xp_total.desc())
        )
        return self._paginar(query, page, size)

    def ranking_carimbos(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                Usuario.id,
                Usuario.nome,
                func.count(UsuarioCarimbo.id).label("total"),
            )
            .join(UsuarioCarimbo, UsuarioCarimbo.usuario_id == Usuario.id)
            .group_by(Usuario.id, Usuario.nome)
            .order_by(func.count(UsuarioCarimbo.id).desc())
        )
        return self._paginar(query, page, size)

    def ranking_checkins(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                Usuario.id,
                Usuario.nome,
                func.count(func.distinct(Checkin.ponto_turistico_id)).label("total"),
            )
            .join(Checkin, Checkin.usuario_id == Usuario.id)
            .group_by(Usuario.id, Usuario.nome)
            .order_by(func.count(func.distinct(Checkin.ponto_turistico_id)).desc())
        )
        return self._paginar(query, page, size)

    def ranking_eco(self, page: int, size: int) -> list[tuple]:
        query = (
            self.db.query(
                Usuario.id,
                Usuario.nome,
                func.coalesce(func.sum(UsuarioEcoAtividade.pontuacao), 0).label("total"),
            )
            .join(UsuarioEcoAtividade, UsuarioEcoAtividade.usuario_id == Usuario.id)
            .group_by(Usuario.id, Usuario.nome)
            .order_by(func.sum(UsuarioEcoAtividade.pontuacao).desc())
        )
        return self._paginar(query, page, size)
