from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.apresentacao.dependencias import (
    obter_cache_commerce,
    obter_repositorio_cupom,
    obter_repositorio_loja,
    obter_servico_cupom,
)
from app.apresentacao.esquemas import CupomResgateRequest, EstoqueResponse, ProdutoResponse, TipoProdutoResponse
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

roteador = APIRouter()


@roteador.get("/produtos", response_model=list[ProdutoResponse], tags=["commerce"])
def list_produtos(loja: RepositorioLojaComCache = Depends(obter_repositorio_loja)):
    return loja.listar_produtos()


@roteador.get("/tipos-produto", response_model=list[TipoProdutoResponse], tags=["commerce"])
def list_tipos_produto(loja: RepositorioLojaComCache = Depends(obter_repositorio_loja)):
    return loja.listar_tipos()


@roteador.get("/estoque", response_model=list[EstoqueResponse], tags=["commerce"])
def list_estoque(loja: RepositorioLojaComCache = Depends(obter_repositorio_loja)):
    return loja.listar_estoque()


@roteador.get("/cupons/disponiveis", tags=["commerce"])
def cupons_disponiveis(
    parceiro_id: int | None = None,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.listar_disponiveis(parceiro_id)
    return {"success": True, "data": dados}


@roteador.get("/cupons/resgatados/{usuario_id}", tags=["commerce"])
def cupons_resgatados(
    usuario_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    uid = resolver_usuario_escopo(usuario, usuario_id)
    dados = servico.listar_resgatados(uid)
    return {"success": True, "data": dados}


@roteador.get("/cupons/verificar", tags=["commerce"])
def verificar_cupom(
    cupom_id: int,
    usuario_id: int,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    repositorio: RepositorioCupom = Depends(obter_repositorio_cupom),
):
    validar_consulta_cupom_usuario(usuario, usuario_id)
    ja = repositorio.ja_resgatado(cupom_id, usuario_id)
    return {"success": True, "jaResgatado": ja}


@roteador.post("/cupons/resgatar", tags=["commerce"])
def resgatar_cupom(
    payload: CupomResgateRequest,
    usuario: UsuarioToken = Depends(obter_usuario_obrigatorio_do_token),
    servico: ServicoCupom = Depends(obter_servico_cupom),
    cache: ServicoCache = Depends(obter_cache_commerce),
):
    validar_resgate_cupom(usuario, payload.usuario_id, payload.parceiro_id)
    resultado = servico.resgatar(payload.cupom_id, payload.usuario_id, payload.parceiro_id)
    cache.invalidar(f"cupons:resgatados:{payload.usuario_id}")
    cache.invalidar(f"cupons:disponiveis:{payload.parceiro_id or 'all'}")
    return resultado


@roteador.get("/cupons/campanhas-parceiro/{parceiro_id}", tags=["commerce"])
def campanhas_parceiro(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.campanhas_parceiro(parceiro_id)
    return {"success": True, "data": dados}


@roteador.get("/cupons/contagem-campanha/{parceiro_id}", tags=["commerce"])
def contagem_campanha(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.contagem_por_campanha(parceiro_id)
    return {"success": True, "data": dados}
