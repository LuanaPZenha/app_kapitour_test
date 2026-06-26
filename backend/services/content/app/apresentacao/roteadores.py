from fastapi import APIRouter, Depends, HTTPException, Query

from app.apresentacao.dependencias import (
    obter_servico_categorias,
    obter_servico_pontos,
    obter_servico_rotas,
)
from app.apresentacao.esquemas import CategoriaResponse, PontoTuristicoResponse, RotaPontoResponse, RotaResponse
from app.apresentacao.mapeadores import montar_pontos_da_rota
from app.dominio.casos_de_uso.servicos import ServicoCategorias, ServicoPontos, ServicoRotas
from kapitour_shared.autenticacao import validar_chave_interna

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "content"}


@roteador.get("/categorias", response_model=list[CategoriaResponse])
def list_categorias(servico: ServicoCategorias = Depends(obter_servico_categorias)):
    return servico.listar()


@roteador.get("/pontos-turisticos", response_model=list[PontoTuristicoResponse])
def list_pontos(
    categoria_id: int | None = Query(default=None),
    servico: ServicoPontos = Depends(obter_servico_pontos),
):
    return servico.listar(categoria_id)


@roteador.get("/pontos-turisticos/{ponto_id}", response_model=PontoTuristicoResponse)
def get_ponto(ponto_id: int, servico: ServicoPontos = Depends(obter_servico_pontos)):
    ponto = servico.buscar_por_id(ponto_id)
    if not ponto:
        raise HTTPException(status_code=404, detail="Ponto não encontrado")
    return ponto


@roteador.get("/internal/pontos/batch", response_model=list[PontoTuristicoResponse])
def internal_batch_pontos(
    ids: str = Query(...),
    _: None = Depends(validar_chave_interna),
    servico: ServicoPontos = Depends(obter_servico_pontos),
):
    ids_pontos = [int(x) for x in ids.split(",") if x.strip()]
    return servico.buscar_por_ids(ids_pontos)


@roteador.get("/ponto-categoria")
def list_ponto_categoria(
    ponto_id: int | None = None,
    categoria_id: int | None = None,
    ponto_ids: str | None = None,
    servico: ServicoPontos = Depends(obter_servico_pontos),
):
    ids = [int(x) for x in ponto_ids.split(",") if x.strip()] if ponto_ids else None
    return servico.listar_ponto_categoria(
        ponto_id=ponto_id,
        categoria_id=categoria_id,
        ponto_ids=ids,
    )


@roteador.get("/rotas", response_model=list[RotaResponse])
def list_rotas(servico: ServicoRotas = Depends(obter_servico_rotas)):
    return servico.listar()


@roteador.get("/rotas/{rota_id}/pontos")
def rotas_pontos(rota_id: int, servico: ServicoRotas = Depends(obter_servico_rotas)):
    relacoes, ids_pontos, pontos = servico.pontos_da_rota(rota_id)
    return montar_pontos_da_rota(relacoes, ids_pontos, pontos)


@roteador.get("/rota-ponto")
def list_rota_ponto(
    rota_id: int | None = None,
    ponto_ids: str | None = None,
    servico: ServicoRotas = Depends(obter_servico_rotas),
):
    ids = [int(x) for x in ponto_ids.split(",") if x.strip()] if ponto_ids else None
    relacoes = servico.listar_rota_ponto(rota_id=rota_id, ponto_ids=ids)
    return [RotaPontoResponse.model_validate(r) for r in relacoes]
