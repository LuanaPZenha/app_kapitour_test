from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import PontoCategoria
from app.repositories import (
    CategoryRepository,
    CouponRepository,
    FavoriteRepository,
    PlaceRepository,
    RatingRepository,
    RouteRepository,
    StoreRepository,
)
from app.schemas import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    AvaliacaoUpdate,
    CategoriaResponse,
    CheckinRequest,
    CupomResgateRequest,
    DiarioCreate,
    EcoRegistrarRequest,
    EstoqueResponse,
    FavoritoCreate,
    FavoritoResponse,
    LoginRequest,
    MessageResponse,
    PontoAvaliacaoCreate,
    PontoTuristicoResponse,
    ProdutoResponse,
    RegisterRequest,
    RotaPontoResponse,
    RotaResponse,
    TipoProdutoResponse,
    TokenResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.services import (
    AuthService,
    CollectionService,
    CouponService,
    DiaryService,
    EcoService,
    FavoriteService,
    GamificationService,
    MissionService,
    RankingService,
    TreasureService,
    UserService,
)

router = APIRouter()


def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1)
    return get_current_user(db, token)


def get_required_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):
    user = get_optional_user(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return user


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).register(
            nome=payload.nome,
            email=payload.email,
            password=payload.password,
            cpf=payload.cpf,
            sexo=payload.sexo,
            data_nascimento=payload.data_nascimento,
        )
        return TokenResponse(access_token=result["access_token"], user=result["user"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).login(payload.email, payload.password)
        return TokenResponse(access_token=result["access_token"], user=result["user"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/auth/me", response_model=UsuarioResponse)
def me(user=Depends(get_required_user)):
    return user


@router.get("/usuarios/email-exists")
def email_exists(email: str, db: Session = Depends(get_db)):
    from app.repositories import UserRepository

    return {"exists": UserRepository(db).email_exists(email)}


@router.get("/usuarios/by-auth/{auth_id}", response_model=UsuarioResponse)
def get_user_by_auth(auth_id: str, db: Session = Depends(get_db)):
    user = UserService(db).get_by_auth_id(auth_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.patch("/usuarios/{auth_id}", response_model=UsuarioResponse)
def update_user(auth_id: str, payload: UsuarioUpdateRequest, db: Session = Depends(get_db)):
    try:
        return UserService(db).update(auth_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/categorias", response_model=list[CategoriaResponse])
def list_categorias(db: Session = Depends(get_db)):
    return CategoryRepository(db).list_all()


@router.get("/pontos-turisticos", response_model=list[PontoTuristicoResponse])
def list_pontos(categoria_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    return PlaceRepository(db).list_all(categoria_id)


@router.get("/pontos-turisticos/{ponto_id}", response_model=PontoTuristicoResponse)
def get_ponto(ponto_id: int, db: Session = Depends(get_db)):
    ponto = PlaceRepository(db).get_by_id(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
    return ponto


@router.get("/ponto-categoria")
def list_ponto_categoria(
    ponto_id: int | None = None,
    categoria_id: int | None = None,
    ponto_ids: str | None = None,
    db: Session = Depends(get_db),
):
    repo = PlaceRepository(db)
    if ponto_id:
        rows = repo.get_ponto_categorias([ponto_id])
    elif ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        rows = repo.get_ponto_categorias(ids)
    elif categoria_id:
        rows = db.query(PontoCategoria).filter(PontoCategoria.categoria_id == categoria_id).all()
    else:
        rows = []
    return [{"ponto_id": row.ponto_id, "categoria_id": row.categoria_id} for row in rows]


@router.get("/rotas", response_model=list[RotaResponse])
def list_rotas(db: Session = Depends(get_db)):
    return RouteRepository(db).list_all()


@router.get("/rotas/{rota_id}/pontos")
def rotas_pontos(rota_id: int, db: Session = Depends(get_db)):
    repo = RouteRepository(db)
    rels = repo.get_rota_pontos(rota_id)
    ponto_ids = [r.ponto_id for r in rels]
    pontos = {p.id: p for p in PlaceRepository(db).get_by_ids(ponto_ids)}
    return {
        "relacionamentos": [RotaPontoResponse.model_validate(r) for r in rels],
        "pontos": [PontoTuristicoResponse.model_validate(pontos[pid]) for pid in ponto_ids if pid in pontos],
    }


@router.get("/rota-ponto")
def list_rota_ponto(
    rota_id: int | None = None,
    ponto_ids: str | None = None,
    db: Session = Depends(get_db),
):
    repo = RouteRepository(db)
    if rota_id:
        return [RotaPontoResponse.model_validate(r) for r in repo.get_rota_pontos(rota_id)]
    if ponto_ids:
        ids = [int(x) for x in ponto_ids.split(",") if x.strip()]
        return [RotaPontoResponse.model_validate(r) for r in repo.get_rota_pontos_by_ponto_ids(ids)]
    return []


@router.get("/favoritos")
def list_favoritos(usuario_id: int, db: Session = Depends(get_db)):
    return FavoriteService(db).list_with_places(usuario_id)


@router.post("/favoritos", response_model=FavoritoResponse)
def create_favorito(payload: FavoritoCreate, db: Session = Depends(get_db)):
    fav = FavoriteRepository(db).create(payload.usuario_id, payload.ponto_id)
    return fav


@router.delete("/favoritos")
def delete_favorito(usuario_id: int, ponto_id: int, db: Session = Depends(get_db)):
    ok = FavoriteRepository(db).delete(usuario_id, ponto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    return {"success": True}


@router.get("/avaliacoes")
def list_avaliacoes(
    ponto_id: int | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
):
    repo = RatingRepository(db)
    if usuario_id and ponto_id:
        item = repo.get_user_rating(usuario_id, ponto_id)
        return item
    if ponto_id:
        return [AvaliacaoResponse.model_validate(a) for a in repo.list_by_ponto(ponto_id)]
    return []


@router.post("/avaliacoes", response_model=AvaliacaoResponse)
def create_avaliacao(payload: AvaliacaoCreate, db: Session = Depends(get_db)):
    repo = RatingRepository(db)
    existing = repo.get_user_rating(payload.usuario_id, payload.ponto_id)
    if existing:
        item = repo.update(existing, payload.nota, payload.comentario)
    else:
        item = repo.create(payload.usuario_id, payload.ponto_id, payload.nota, payload.comentario)
    return item


@router.put("/avaliacoes/{avaliacao_id}", response_model=AvaliacaoResponse)
def update_avaliacao(avaliacao_id: int, payload: AvaliacaoUpdate, db: Session = Depends(get_db)):
    from app.models import Avaliacao

    avaliacao = db.query(Avaliacao).filter(Avaliacao.id == avaliacao_id).first()
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return RatingRepository(db).update(avaliacao, payload.nota, payload.comentario)


@router.post("/ponto-avaliacoes")
def create_ponto_avaliacao(payload: PontoAvaliacaoCreate, db: Session = Depends(get_db)):
    item = RatingRepository(db).create_ponto_avaliacao(
        payload.ponto_id, payload.usuario_id, payload.nota, payload.comentario
    )
    return item


@router.get("/ponto-avaliacoes/media")
def media_ponto_avaliacoes(ponto_id: int, db: Session = Depends(get_db)):
    ratings = RatingRepository(db).list_ponto_avaliacoes(ponto_id)
    if not ratings:
        return {"media": 0}
    media = sum(r.nota for r in ratings) / len(ratings)
    return {"media": round(media, 1)}


@router.get("/produtos", response_model=list[ProdutoResponse])
def list_produtos(db: Session = Depends(get_db)):
    return StoreRepository(db).list_produtos()


@router.get("/tipos-produto", response_model=list[TipoProdutoResponse])
def list_tipos_produto(db: Session = Depends(get_db)):
    return StoreRepository(db).list_tipos()


@router.get("/estoque", response_model=list[EstoqueResponse])
def list_estoque(db: Session = Depends(get_db)):
    return StoreRepository(db).list_estoque()


@router.get("/cupons/disponiveis")
def cupons_disponiveis(parceiro_id: int | None = None, db: Session = Depends(get_db)):
    data = CouponService(db).list_available(parceiro_id)
    return {"success": True, "data": data}


@router.get("/cupons/resgatados/{usuario_id}")
def cupons_resgatados(usuario_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).list_resgatados(usuario_id)
    return {"success": True, "data": data}


@router.get("/cupons/verificar")
def verificar_cupom(cupom_id: int, usuario_id: int, db: Session = Depends(get_db)):
    ja = CouponRepository(db).already_redeemed(cupom_id, usuario_id)
    return {"success": True, "jaResgatado": ja}


@router.post("/cupons/resgatar")
def resgatar_cupom(payload: CupomResgateRequest, db: Session = Depends(get_db)):
    result = CouponService(db).redeem(payload.cupom_id, payload.usuario_id, payload.parceiro_id)
    return result


@router.get("/cupons/campanhas-parceiro/{parceiro_id}")
def campanhas_parceiro(parceiro_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).campanhas_parceiro(parceiro_id)
    return {"success": True, "data": data}


@router.get("/cupons/contagem-campanha/{parceiro_id}")
def contagem_campanha(parceiro_id: int, db: Session = Depends(get_db)):
    data = CouponService(db).contagem_por_campanha(parceiro_id)
    return {"success": True, "data": data}


# ─────────────────────────────────────────────────────────────
# KapiPass — Passaporte Turístico Gamificado
# ─────────────────────────────────────────────────────────────


@router.get("/kapipass/me")
def kapipass_me(user=Depends(get_required_user), db: Session = Depends(get_db)):
    return GamificationService(db).get_passaporte(user.id)


@router.get("/kapipass/niveis")
def kapipass_niveis(db: Session = Depends(get_db)):
    return GamificationService(db).list_niveis()


@router.post("/kapipass/checkin")
def kapipass_checkin(
    payload: CheckinRequest,
    user=Depends(get_required_user),
    db: Session = Depends(get_db),
):
    try:
        return GamificationService(db).processar_checkin(
            usuario_id=user.id,
            ponto_id=payload.ponto_turistico_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/checkins")
def kapipass_checkins(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_checkins(usuario_id)


@router.get("/kapipass/carimbos")
def kapipass_carimbos(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_carimbos(usuario_id)


@router.get("/kapipass/conquistas")
def kapipass_conquistas(usuario_id: int, db: Session = Depends(get_db)):
    return GamificationService(db).list_conquistas(usuario_id)


@router.get("/kapipass/colecoes")
def kapipass_colecoes(usuario_id: int, db: Session = Depends(get_db)):
    return CollectionService(db).list_colecoes(usuario_id)


@router.get("/kapipass/missoes")
def kapipass_missoes(usuario_id: int, db: Session = Depends(get_db)):
    return MissionService(db).list_missoes(usuario_id)


@router.post("/kapipass/missoes/{missao_id}/aceitar")
def kapipass_aceitar_missao(
    missao_id: int,
    user=Depends(get_required_user),
    db: Session = Depends(get_db),
):
    try:
        return MissionService(db).aceitar(user.id, missao_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/eco")
def kapipass_eco(usuario_id: int, db: Session = Depends(get_db)):
    return EcoService(db).list_atividades(usuario_id)


@router.post("/kapipass/eco/registrar")
def kapipass_eco_registrar(
    payload: EcoRegistrarRequest,
    user=Depends(get_required_user),
    db: Session = Depends(get_db),
):
    try:
        return EcoService(db).registrar(user.id, payload.eco_atividade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/diario")
def kapipass_diario(usuario_id: int, db: Session = Depends(get_db)):
    return DiaryService(db).list_entradas(usuario_id)


@router.post("/kapipass/diario")
def kapipass_diario_criar(
    payload: DiarioCreate,
    user=Depends(get_required_user),
    db: Session = Depends(get_db),
):
    return DiaryService(db).criar(
        usuario_id=user.id,
        ponto_turistico_id=payload.ponto_turistico_id,
        checkin_id=payload.checkin_id,
        comentario=payload.comentario,
        foto=payload.foto,
    )


@router.get("/kapipass/tesouros")
def kapipass_tesouros(usuario_id: int, db: Session = Depends(get_db)):
    return TreasureService(db).list_tesouros(usuario_id)


@router.post("/kapipass/tesouros/{tesouro_id}/concluir")
def kapipass_concluir_tesouro(
    tesouro_id: int,
    user=Depends(get_required_user),
    db: Session = Depends(get_db),
):
    try:
        return TreasureService(db).concluir(user.id, tesouro_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/kapipass/rankings")
def kapipass_rankings(
    categoria: str = Query(default="exploradores"),
    page: int = Query(default=1),
    size: int = Query(default=20),
    db: Session = Depends(get_db),
):
    return RankingService(db).get_ranking(categoria, page, size)
