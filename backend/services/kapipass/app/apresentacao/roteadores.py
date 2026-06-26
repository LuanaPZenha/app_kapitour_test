from fastapi import APIRouter, Depends, HTTPException, Query

from app.apresentacao.dependencias import (
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
from kapitour_shared.autenticacao import UsuarioToken, obter_usuario_obrigatorio_do_token

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "kapipass"}


@roteador.get("/kapipass/me")
def kapipass_me(
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    try:
        return servico.obter_passaporte(usuario.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/niveis")
def kapipass_niveis(servico: ServicoGamificacao = Depends(obter_servico_gamificacao)):
    return servico.listar_niveis()


@roteador.post("/kapipass/checkin")
def kapipass_checkin(
    payload: CheckinRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    try:
        return servico.processar_checkin(
            usuario_id=usuario.id,
            ponto_id=payload.ponto_turistico_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/checkins")
def kapipass_checkins(
    usuario_id: int,
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    return servico.listar_checkins(usuario_id)


@roteador.get("/kapipass/carimbos")
def kapipass_carimbos(
    usuario_id: int,
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    return servico.listar_carimbos(usuario_id)


@roteador.get("/kapipass/conquistas")
def kapipass_conquistas(
    usuario_id: int,
    servico: ServicoGamificacao = Depends(obter_servico_gamificacao),
):
    return servico.listar_conquistas(usuario_id)


@roteador.get("/kapipass/colecoes")
def kapipass_colecoes(
    usuario_id: int,
    servico: ServicoColecao = Depends(obter_servico_colecao),
):
    return servico.listar_colecoes(usuario_id)


@roteador.get("/kapipass/missoes")
def kapipass_missoes(
    usuario_id: int,
    servico: ServicoMissao = Depends(obter_servico_missao),
):
    return servico.listar_missoes(usuario_id)


@roteador.post("/kapipass/missoes/{missao_id}/aceitar")
def kapipass_aceitar_missao(
    missao_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoMissao = Depends(obter_servico_missao),
):
    try:
        return servico.aceitar(usuario.id, missao_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/eco")
def kapipass_eco(
    usuario_id: int,
    servico: ServicoEco = Depends(obter_servico_eco),
):
    return servico.listar_atividades(usuario_id)


@roteador.post("/kapipass/eco/registrar")
def kapipass_eco_registrar(
    payload: EcoRegistrarRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoEco = Depends(obter_servico_eco),
):
    try:
        return servico.registrar(usuario.id, payload.eco_atividade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/diario")
def kapipass_diario(
    usuario_id: int,
    servico: ServicoDiario = Depends(obter_servico_diario),
):
    return servico.listar_entradas(usuario_id)


@roteador.post("/kapipass/diario")
def kapipass_diario_criar(
    payload: DiarioCreate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoDiario = Depends(obter_servico_diario),
):
    return servico.criar(
        usuario_id=usuario.id,
        ponto_turistico_id=payload.ponto_turistico_id,
        checkin_id=payload.checkin_id,
        comentario=payload.comentario,
        foto=payload.foto,
    )


@roteador.get("/kapipass/tesouros")
def kapipass_tesouros(
    usuario_id: int,
    servico: ServicoTesouro = Depends(obter_servico_tesouro),
):
    return servico.listar_tesouros(usuario_id)


@roteador.post("/kapipass/tesouros/{tesouro_id}/concluir")
def kapipass_concluir_tesouro(
    tesouro_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoTesouro = Depends(obter_servico_tesouro),
):
    try:
        return servico.concluir(usuario.id, tesouro_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/rankings")
def kapipass_rankings(
    categoria: str = Query(default="exploradores"),
    page: int = Query(default=1),
    size: int = Query(default=20),
    servico: ServicoRanking = Depends(obter_servico_ranking),
):
    return servico.obter_ranking(categoria, page, size)
