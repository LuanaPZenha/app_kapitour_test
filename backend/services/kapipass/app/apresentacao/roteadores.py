from fastapi import APIRouter, Depends, HTTPException, Query

from app.apresentacao.dependencias import (
    obter_cache_kapipass,
    obter_servico_colecao,
    obter_servico_diario,
    obter_servico_eco,
    obter_servico_gamificacao,
    obter_servico_missao,
    obter_servico_ranking,
    obter_servico_tesouro,
)
from app.apresentacao.esquemas import CheckinRequest, DiarioCreate, EcoRegistrarRequest
from app.aplicacao.servicos import (
    ServicoColecao,
    ServicoDiario,
    ServicoEco,
    ServicoGamificacao,
    ServicoMissao,
    ServicoRanking,
    ServicoTesouro,
)
from app.infraestrutura.cache.servicos_cache import invalidar_cache_usuario
from kapitour_shared.autenticacao import (
    UsuarioToken,
    obter_usuario_obrigatorio_do_token,
    resolver_usuario_escopo,
)
from kapitour_shared.cache.cache_service import ServicoCache

roteador = APIRouter()


@roteador.get("/kapipass/me", tags=["kapipass"], summary="Passaporte e progresso do usuário autenticado")
def kapipass_me(
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    try:
        return servico.obter_passaporte(usuario.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/niveis", tags=["kapipass"])
def kapipass_niveis(servico: ServicoGamificacao = Depends(obter_servico_gamificacao)):
    return servico.listar_niveis()


@roteador.post(
    "/kapipass/checkin",
    tags=["kapipass"],
    summary="Registrar check-in em ponto turístico",
    responses={400: {"description": "Check-in inválido ou duplicado"}},
)
def kapipass_checkin(
    payload: CheckinRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
):
    try:
        resultado = servico.processar_checkin(
            usuario_id=usuario.id,
            ponto_id=payload.ponto_turistico_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        invalidar_cache_usuario(cache, usuario.id)
        return resultado
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/checkins", tags=["kapipass"])
def kapipass_checkins(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_checkins(uid)


@roteador.get("/kapipass/carimbos", tags=["kapipass"])
def kapipass_carimbos(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_carimbos(uid)


@roteador.get("/kapipass/conquistas", tags=["kapipass"])
def kapipass_conquistas(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_conquistas(uid)


@roteador.get("/kapipass/colecoes", tags=["kapipass"])
def kapipass_colecoes(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoColecao = Depends(obter_servico_colecao),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_colecoes(uid)


@roteador.get("/kapipass/missoes", tags=["kapipass"])
def kapipass_missoes(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoMissao = Depends(obter_servico_missao),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_missoes(uid)


@roteador.post("/kapipass/missoes/{missao_id}/aceitar", tags=["kapipass"])
def kapipass_aceitar_missao(
    missao_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoMissao = Depends(obter_servico_missao),
    cache: ServicoCache = Depends(obter_cache_kapipass),
):
    try:
        resultado = servico.aceitar(usuario.id, missao_id)
        invalidar_cache_usuario(cache, usuario.id)
        return resultado
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/eco", tags=["kapipass"])
def kapipass_eco(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoEco = Depends(obter_servico_eco),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_atividades(uid)


@roteador.post("/kapipass/eco/registrar", tags=["kapipass"])
def kapipass_eco_registrar(
    payload: EcoRegistrarRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoEco = Depends(obter_servico_eco),
    cache: ServicoCache = Depends(obter_cache_kapipass),
):
    try:
        resultado = servico.registrar(usuario.id, payload.eco_atividade_id)
        invalidar_cache_usuario(cache, usuario.id)
        return resultado
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/diario", tags=["kapipass"])
def kapipass_diario(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoDiario = Depends(obter_servico_diario),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_entradas(uid)


@roteador.post("/kapipass/diario", tags=["kapipass"])
def kapipass_diario_criar(
    payload: DiarioCreate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoDiario = Depends(obter_servico_diario),
    cache: ServicoCache = Depends(obter_cache_kapipass),
):
    resultado = servico.criar(
        usuario_id=usuario.id,
        ponto_turistico_id=payload.ponto_turistico_id,
        checkin_id=payload.checkin_id,
        comentario=payload.comentario,
        foto=payload.foto,
    )
    invalidar_cache_usuario(cache, usuario.id)
    return resultado


@roteador.get("/kapipass/tesouros", tags=["kapipass"])
def kapipass_tesouros(
    usuario_id: int | None = None,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoTesouro = Depends(obter_servico_tesouro),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_tesouros(uid)


@roteador.post("/kapipass/tesouros/{tesouro_id}/concluir", tags=["kapipass"])
def kapipass_concluir_tesouro(
    tesouro_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoTesouro = Depends(obter_servico_tesouro),
    cache: ServicoCache = Depends(obter_cache_kapipass),
):
    try:
        resultado = servico.concluir(usuario.id, tesouro_id)
        invalidar_cache_usuario(cache, usuario.id)
        return resultado
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get(
    "/kapipass/rankings",
    tags=["kapipass"],
    summary="Ranking de jogadores por categoria",
    responses={
        200: {
            "description": "Ranking paginado. Aceita `pagina`/`tamanho` ou `page`/`size` (legado).",
        }
    },
)
def kapipass_rankings(
    categoria: str = Query(default="exploradores", description="exploradores, carimbos, eco ou xp"),
    pagina: int | None = Query(default=None, ge=1, description="Número da página"),
    tamanho: int | None = Query(default=None, ge=1, le=100, description="Itens por página"),
    page: int = Query(default=1, ge=1, description="Alias legado para pagina"),
    size: int = Query(default=20, ge=1, le=100, description="Alias legado para tamanho"),
    servico: ServicoRanking = Depends(obter_servico_ranking),
):
    pagina_efetiva = pagina if pagina is not None else page
    tamanho_efetivo = tamanho if tamanho is not None else size
    return servico.obter_ranking(categoria, pagina_efetiva, tamanho_efetivo)
