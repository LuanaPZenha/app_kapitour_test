from contextlib import asynccontextmanager

from app.migracoes import executar_migracoes, semear_dados_iniciais
from app.roteadores import roteador
from kapitour_shared.banco_dados import FabricaSessao
from kapitour_shared.configuracao import configuracoes
from kapitour_shared.core.app_factory import criar_aplicacao


@asynccontextmanager
async def lifespan(_):
    executar_migracoes()
    sessao = FabricaSessao()
    try:
        semear_dados_iniciais(sessao)
    finally:
        sessao.close()
    yield


configuracoes.service_name = "auth"

app = criar_aplicacao(
    titulo="Kapitour Auth Service",
    versao="2.0.0",
    lifespan=lifespan,
    descricao="Autenticação JWT, refresh tokens, RBAC e gestão de usuários.",
)

app.include_router(roteador, prefix="/api")
