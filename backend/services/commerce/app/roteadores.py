from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencias import obter_repositorio_cupom, obter_servico_cupom
from app.esquemas import CupomResgateRequest, EstoqueResponse, ProdutoResponse, TipoProdutoResponse
from app.repositorios import RepositorioCupom, RepositorioLoja
from app.servicos import ServicoCupom
from kapitour_shared.banco_dados import obter_sessao_banco

roteador = APIRouter()


@roteador.get("/health")
def health():
    return {"status": "ok", "service": "commerce"}


@roteador.get("/produtos", response_model=list[ProdutoResponse])
def list_produtos(sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioLoja(sessao).listar_produtos()


@roteador.get("/tipos-produto", response_model=list[TipoProdutoResponse])
def list_tipos_produto(sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioLoja(sessao).listar_tipos()


@roteador.get("/estoque", response_model=list[EstoqueResponse])
def list_estoque(sessao: Session = Depends(obter_sessao_banco)):
    return RepositorioLoja(sessao).listar_estoque()


@roteador.get("/cupons/disponiveis")
def cupons_disponiveis(
    parceiro_id: int | None = None,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.listar_disponiveis(parceiro_id)
    return {"success": True, "data": dados}


@roteador.get("/cupons/resgatados/{usuario_id}")
def cupons_resgatados(
    usuario_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.listar_resgatados(usuario_id)
    return {"success": True, "data": dados}


@roteador.get("/cupons/verificar")
def verificar_cupom(
    cupom_id: int,
    usuario_id: int,
    repositorio: RepositorioCupom = Depends(obter_repositorio_cupom),
):
    ja = repositorio.ja_resgatado(cupom_id, usuario_id)
    return {"success": True, "jaResgatado": ja}


@roteador.post("/cupons/resgatar")
def resgatar_cupom(
    payload: CupomResgateRequest,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    return servico.resgatar(payload.cupom_id, payload.usuario_id, payload.parceiro_id)


@roteador.get("/cupons/campanhas-parceiro/{parceiro_id}")
def campanhas_parceiro(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.campanhas_parceiro(parceiro_id)
    return {"success": True, "data": dados}


@roteador.get("/cupons/contagem-campanha/{parceiro_id}")
def contagem_campanha(
    parceiro_id: int,
    servico: ServicoCupom = Depends(obter_servico_cupom),
):
    dados = servico.contagem_por_campanha(parceiro_id)
    return {"success": True, "data": dados}
