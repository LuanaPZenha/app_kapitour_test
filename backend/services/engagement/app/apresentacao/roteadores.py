from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.apresentacao.dependencias import (
    obter_cache_engagement,
    obter_repositorio_avaliacao,
    obter_repositorio_favorito,
    obter_servico_avaliacao,
    obter_servico_favoritos,
)
from app.apresentacao.esquemas import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    AvaliacaoUpdate,
    FavoritoCreate,
    FavoritoResponse,
    PontoAvaliacaoCreate,
)
from app.dominio.casos_de_uso.servicos import ServicoAvaliacao, ServicoFavoritos
from app.infraestrutura.persistencia.repositorios import RepositorioAvaliacao, RepositorioFavorito
from kapitour_shared.autenticacao import (
    UsuarioToken,
    obter_usuario_obrigatorio_do_token,
    obter_usuario_opcional_do_token,
    resolver_usuario_escopo,
)
from kapitour_shared.cache.cache_service import ServicoCache

roteador = APIRouter()


def _invalidar_favoritos(cache: ServicoCache, usuario_id: int) -> None:
    cache.invalidar(f"favoritos:{usuario_id}")


def _invalidar_avaliacoes_ponto(cache: ServicoCache, ponto_id: int) -> None:
    cache.invalidar(f"avaliacoes:ponto:{ponto_id}")
    cache.invalidar(f"avaliacoes:media:{ponto_id}")


@roteador.get(
    "/favoritos",
    tags=["engajamento"],
    summary="Listar favoritos do usuário",
    responses={401: {"description": "Token ausente ou inválido"}},
)
def list_favoritos(
    usuario_id: int | None = Query(default=None, description="Legado — omita para usar o JWT"),
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoFavoritos = Depends(obter_servico_favoritos),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    return servico.listar_com_pontos(uid)


@roteador.post(
    "/favoritos",
    response_model=FavoritoResponse,
    tags=["engajamento"],
    summary="Adicionar ponto aos favoritos",
    responses={401: {"description": "Não autenticado"}},
)
def create_favorito(
    payload: FavoritoCreate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
    cache: ServicoCache = Depends(obter_cache_engagement),
):
    uid = resolver_usuario_escopo(usuario, payload.usuario_id)
    resultado = repositorio.criar(uid, payload.ponto_id)
    _invalidar_favoritos(cache, uid)
    return resultado


@roteador.delete("/favoritos", tags=["engajamento"])
def delete_favorito(
    ponto_id: int,
    usuario_id: int | None = Query(default=None, description="Legado — omita para usar o JWT"),
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    repositorio: RepositorioFavorito = Depends(obter_repositorio_favorito),
    cache: ServicoCache = Depends(obter_cache_engagement),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    ok = repositorio.excluir(uid, ponto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    _invalidar_favoritos(cache, uid)
    return {"success": True}


@roteador.get(
    "/avaliacoes",
    tags=["engajamento"],
    summary="Listar avaliações por ponto ou usuário",
    responses={401: {"description": "Necessário ao filtrar por usuario_id"}},
)
def list_avaliacoes(
    ponto_id: int | None = None,
    usuario_id: int | None = None,
    usuario: UsuarioToken | None = Depends(obter_usuario_opcional_do_token),
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    if usuario_id is not None:
        if not usuario:
            raise HTTPException(status_code=401, detail="Não autenticado")
        usuario_id = resolver_usuario_escopo(usuario, usuario_id)
    elif usuario and ponto_id is not None:
        usuario_id = usuario.id
    resultado = servico.listar(ponto_id=ponto_id, usuario_id=usuario_id)
    if usuario_id and ponto_id:
        return resultado
    if ponto_id:
        return [AvaliacaoResponse.model_validate(a) for a in resultado]
    return []


@roteador.post("/avaliacoes", response_model=AvaliacaoResponse, tags=["engajamento"])
def create_avaliacao(
    payload: AvaliacaoCreate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
    cache: ServicoCache = Depends(obter_cache_engagement),
):
    uid = resolver_usuario_escopo(usuario, payload.usuario_id)
    item = servico.criar_ou_atualizar(uid, payload.ponto_id, payload.nota, payload.comentario)
    _invalidar_avaliacoes_ponto(cache, payload.ponto_id)
    return item


@roteador.put("/avaliacoes/{avaliacao_id}", response_model=AvaliacaoResponse, tags=["engajamento"])
def update_avaliacao(
    avaliacao_id: int,
    payload: AvaliacaoUpdate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
    repositorio: RepositorioAvaliacao = Depends(obter_repositorio_avaliacao),
    cache: ServicoCache = Depends(obter_cache_engagement),
):
    existente = repositorio.buscar_por_id(avaliacao_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    if existente.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Não autorizado a alterar esta avaliação")
    item = servico.atualizar_por_id(avaliacao_id, payload.nota, payload.comentario)
    _invalidar_avaliacoes_ponto(cache, existente.ponto_id)
    return item


@roteador.post("/ponto-avaliacoes", tags=["engajamento"])
def create_ponto_avaliacao(
    payload: PontoAvaliacaoCreate,
    authorization: Annotated[str | None, Header()] = None,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
    cache: ServicoCache = Depends(obter_cache_engagement),
):
    usuario_id = payload.usuario_id
    if usuario_id is not None:
        usuario = obter_usuario_obrigatorio_do_token(authorization)
        usuario_id = resolver_usuario_escopo(usuario, usuario_id)
    elif authorization:
        usuario = obter_usuario_obrigatorio_do_token(authorization)
        usuario_id = usuario.id
    resultado = servico.criar_ponto_avaliacao(
        payload.ponto_id, usuario_id, payload.nota, payload.comentario
    )
    _invalidar_avaliacoes_ponto(cache, payload.ponto_id)
    return resultado


@roteador.get(
    "/ponto-avaliacoes/media",
    tags=["engajamento"],
    summary="Média de notas de um ponto turístico",
)
def media_ponto_avaliacoes(
    ponto_id: int,
    servico: ServicoAvaliacao = Depends(obter_servico_avaliacao),
):
    return servico.media_por_ponto(ponto_id)
