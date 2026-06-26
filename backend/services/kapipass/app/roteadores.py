from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.esquemas import CheckinRequest, DiarioCreate, EcoRegistrarRequest
from app.servicos import (
    ServicoColecao,
    ServicoDiario,
    ServicoEco,
    ServicoGamificacao,
    ServicoMissao,
    ServicoRanking,
    ServicoTesouro,
)
from kapitour_shared.autenticacao import UsuarioToken, obter_usuario_obrigatorio_do_token
from kapitour_shared.banco_dados import obter_sessao_banco

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "kapipass"}


@roteador.get("/kapipass/me")
def kapipass_me(
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    try:
        return ServicoGamificacao(sessao).obter_passaporte(usuario.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/niveis")
def kapipass_niveis(sessao: Session = Depends(obter_sessao_banco)):
    return ServicoGamificacao(sessao).listar_niveis()


@roteador.post("/kapipass/checkin")
def kapipass_checkin(
    payload: CheckinRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    try:
        return ServicoGamificacao(sessao).processar_checkin(
            usuario_id=usuario.id,
            ponto_id=payload.ponto_turistico_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/checkins")
def kapipass_checkins(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoGamificacao(sessao).listar_checkins(usuario_id)


@roteador.get("/kapipass/carimbos")
def kapipass_carimbos(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoGamificacao(sessao).listar_carimbos(usuario_id)


@roteador.get("/kapipass/conquistas")
def kapipass_conquistas(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoGamificacao(sessao).listar_conquistas(usuario_id)


@roteador.get("/kapipass/colecoes")
def kapipass_colecoes(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoColecao(sessao).listar_colecoes(usuario_id)


@roteador.get("/kapipass/missoes")
def kapipass_missoes(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoMissao(sessao).listar_missoes(usuario_id)


@roteador.post("/kapipass/missoes/{missao_id}/aceitar")
def kapipass_aceitar_missao(
    missao_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    try:
        return ServicoMissao(sessao).aceitar(usuario.id, missao_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/eco")
def kapipass_eco(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoEco(sessao).listar_atividades(usuario_id)


@roteador.post("/kapipass/eco/registrar")
def kapipass_eco_registrar(
    payload: EcoRegistrarRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    try:
        return ServicoEco(sessao).registrar(usuario.id, payload.eco_atividade_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/diario")
def kapipass_diario(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoDiario(sessao).listar_entradas(usuario_id)


@roteador.post("/kapipass/diario")
def kapipass_diario_criar(
    payload: DiarioCreate,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    return ServicoDiario(sessao).criar(
        usuario_id=usuario.id,
        ponto_turistico_id=payload.ponto_turistico_id,
        checkin_id=payload.checkin_id,
        comentario=payload.comentario,
        foto=payload.foto,
    )


@roteador.get("/kapipass/tesouros")
def kapipass_tesouros(usuario_id: int, sessao: Session = Depends(obter_sessao_banco)):
    return ServicoTesouro(sessao).listar_tesouros(usuario_id)


@roteador.post("/kapipass/tesouros/{tesouro_id}/concluir")
def kapipass_concluir_tesouro(
    tesouro_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    sessao: Session = Depends(obter_sessao_banco),
):
    try:
        return ServicoTesouro(sessao).concluir(usuario.id, tesouro_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@roteador.get("/kapipass/rankings")
def kapipass_rankings(
    categoria: str = Query(default="exploradores"),
    page: int = Query(default=1),
    size: int = Query(default=20),
    sessao: Session = Depends(obter_sessao_banco),
):
    return ServicoRanking(sessao).obter_ranking(categoria, page, size)
