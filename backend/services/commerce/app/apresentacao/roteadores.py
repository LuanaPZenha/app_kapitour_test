from fastapi import APIRouter, Depends, Query

from app.apresentacao.dependencias import (
    obter_cache_commerce,
    obter_repositorio_cupom,
    obter_repositorio_loja,
    obter_servico_cupom,
)
from app.apresentacao.esquemas import (
    CupomResgateRequest,
    EstoqueResponse,
    ProdutoResponse,
    ProdutosPaginadosResponse,
    TipoProdutoResponse,
)
from app.dominio.casos_de_uso.servicos import ServicoCupom
from app.infraestrutura.cache.servicos_cache import RepositorioLojaComCache
from app.infraestrutura.persistencia.repositorios import RepositorioCupom
from kapitour_shared.autenticacao import (
    UsuarioToken,
    obter_usuario_obrigatorio_do_token,
    resolver_usuario_escopo,
    validar_consulta_cupom_usuario,
    validar_resgate_cupom,
)
from kapitour_shared.cache.cache_service import ServicoCache
from kapitour_shared.core.paginacao import montar_resposta_paginada

roteador = APIRouter()


@roteador.get(
    "/produtos",
    tags=["commerce"],
    summary="Listar produtos da loja",
    responses={
        200: {
            "description": "Lista completa (padrão) ou resposta paginada quando `pagina`/`tamanho` são informados",
        }
    },
)
def list_produtos(
    pagina: int | None = Query(default=None, ge=1, description="Número da página (opcional)"),
    tamanho: int | None = Query(default=None, ge=1, le=100, description="Itens por página"),
    loja: RepositorioLojaComCache = Depends(obter_repositorio_loja),
):
    itens = loja.listar_produtos()
    if pagina is None and tamanho is None:
        return itens
    resposta = montar_resposta_paginada(
        [ProdutoResponse.model_validate(p).model_dump() for p in itens],
        pagina or 1,
        tamanho or 20,
    )
    return ProdutosPaginadosResponse.model_validate(resposta)


@roteador.get(
    "/tipos-produto",
    response_model=list[TipoProdutoResponse],
    tags=["commerce"],
    summary="Listar tipos de produto",
)
def list_tipos_produto(loja: RepositorioLojaComCache = Depends(obter_repositorio_loja)):
    return loja.listar_tipos()


@roteador.get(
    "/estoque",
    response_model=list[EstoqueResponse],
    tags=["commerce"],
    summary="Consultar estoque de produtos",
)
def list_estoque(loja: RepositorioLojaComCache = Depends(obter_repositorio_loja)):
    return loja.listar_estoque()


@roteador.get(
    "/cupons/disponiveis",
    tags=["commerce"],
    summary="Listar cupons disponíveis para resgate",
    responses={
        200: {
            "description": "Lista em `data` (padrão) ou objeto paginado em `data` quando `pagina`/`tamanho` são informados",
        }
    },
)
def cupons_disponiveis(
    parceiro_id: int | None = Query(default=None, description="Filtrar por parceiro"),
    pagina: int | None = Query(default=None, ge=1, description="Número da página (opcional)"),
    tamanho: int | None = Query(default=None, ge=1, le=100, description="Itens por página"),
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.listar_disponiveis(parceiro_id)
    if pagina is None and tamanho is None:
        return {"success": True, "data": dados}
    return {"success": True, "data": montar_resposta_paginada(dados, pagina or 1, tamanho or 20)}


@roteador.get(
    "/cupons/resgatados/me",
    tags=["commerce"],
    summary="Cupons resgatados do usuário autenticado",
    responses={401: {"description": "Token ausente ou inválido"}},
)
def cupons_resgatados_me(
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.listar_resgatados(usuario.id)
    return {"success": True, "data": dados}


@roteador.get(
    "/cupons/resgatados/{usuario_id}",
    tags=["commerce"],
    summary="Cupons resgatados (legado — preferir /cupons/resgatados/me)",
    responses={401: {"description": "Token ausente ou inválido"}},
    deprecated=True,
)
def cupons_resgatados(
    usuario_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    dados = servico.listar_resgatados(uid)
    return {"success": True, "data": dados}


@roteador.get(
    "/cupons/verificar",
    tags=["commerce"],
    summary="Verificar se cupom já foi resgatado",
    responses={401: {"description": "Não autenticado"}, 403: {"description": "Sem permissão"}},
)
def verificar_cupom(
    cupom_id: int,
    usuario_id: int | None = Query(default=None, description="Obrigatório para empresa; omita para turista"),
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    repositorio: RepositorioCupom = Depends(obter_repositorio_cupom),
):
    uid = validar_consulta_cupom_usuario(usuario, usuario_id)
    ja = repositorio.ja_resgatado(cupom_id, uid)
    return {"success": True, "jaResgatado": ja}


@roteador.post(
    "/cupons/resgatar",
    tags=["commerce"],
    summary="Resgatar cupom",
    responses={400: {"description": "Cupom indisponível ou já resgatado"}, 403: {"description": "Sem permissão"}},
)
def resgatar_cupom(
    payload: CupomResgateRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoCupom = Depends(obter_servico_cupom),
    cache: ServicoCache = Depends(obter_cache_commerce),
):
    uid = validar_resgate_cupom(usuario, payload.usuario_id, payload.parceiro_id)
    resultado = servico.resgatar(payload.cupom_id, uid, payload.parceiro_id)
    cache.invalidar(f"cupons:resgatados:{uid}")
    cache.invalidar(f"cupons:disponiveis:{payload.parceiro_id or 'all'}")
    return resultado


@roteador.get(
    "/cupons/campanhas-parceiro/{parceiro_id}",
    tags=["commerce"],
    summary="Campanhas ativas do parceiro",
)
def campanhas_parceiro(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.campanhas_parceiro(parceiro_id)
    return {"success": True, "data": dados}


@roteador.get(
    "/cupons/contagem-campanha/{parceiro_id}",
    tags=["commerce"],
    summary="Contagem de cupons resgatados por campanha",
)
def contagem_campanha(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.contagem_por_campanha(parceiro_id)
    return {"success": True, "data": dados}
