from fastapi import APIRouter, Depends, HTTPException, Query

from app.apresentacao.dependencias import (
    obter_servico_categorias,
    obter_servico_pontos,
    obter_servico_rotas,
)
from app.apresentacao.esquemas import (
    CategoriaResponse,
    PontosPaginadosResponse,
    PontoTuristicoResponse,
    RotaPontoResponse,
    RotaResponse,
    RotasPaginadasResponse,
)
from app.apresentacao.mapeadores import montar_pontos_da_rota
from app.dominio.casos_de_uso.servicos import ServicoCategorias, ServicoPontos, ServicoRotas
from kapitour_shared.autenticacao import validar_chave_interna
from kapitour_shared.core.paginacao import montar_resposta_paginada

roteador = APIRouter()


@roteador.get("/health", tags=["health"], summary="Health check do serviço content")
def health():
    return {"status": "ok", "service": "content"}


@roteador.get(
    "/categorias",
    response_model=list[CategoriaResponse],
    tags=["conteudo"],
    summary="Listar categorias de pontos turísticos",
)
def list_categorias(servico: ServicoCategorias = Depends(obter_servico_categorias)):
    return servico.listar()


@roteador.get(
    "/pontos-turisticos",
    response_model=list[PontoTuristicoResponse],
    tags=["conteudo"],
    summary="Listar pontos turísticos",
    responses={
        200: {
            "description": "Lista completa (padrão) ou resposta paginada quando `pagina`/`tamanho` são informados",
        }
    },
)
def list_pontos(
    categoria_id: int | None = Query(default=None, description="Filtrar por categoria"),
    pagina: int | None = Query(default=None, ge=1, description="Número da página (opcional)"),
    tamanho: int | None = Query(default=None, ge=1, le=100, description="Itens por página"),
    servico: ServicoPontos = Depends(obter_servico_pontos),
):
    itens = servico.listar(categoria_id)
    if pagina is None and tamanho is None:
        return itens
    resposta = montar_resposta_paginada([p.model_dump() for p in itens], pagina or 1, tamanho or 20)
    return PontosPaginadosResponse.model_validate(resposta)


@roteador.get(
    "/pontos-turisticos/{ponto_id}",
    response_model=PontoTuristicoResponse,
    tags=["conteudo"],
    summary="Obter ponto turístico por ID",
    responses={404: {"description": "Ponto não encontrado"}},
)
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


@roteador.get("/rotas", tags=["conteudo"], summary="Listar rotas turísticas")
def list_rotas(
    pagina: int | None = Query(default=None, ge=1),
    tamanho: int | None = Query(default=None, ge=1, le=100),
    servico: ServicoRotas = Depends(obter_servico_rotas),
):
    itens = servico.listar()
    if pagina is None and tamanho is None:
        return itens
    resposta = montar_resposta_paginada([r.model_dump() for r in itens], pagina or 1, tamanho or 20)
    return RotasPaginadasResponse.model_validate(resposta)


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
