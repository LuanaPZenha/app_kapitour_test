from contextlib import asynccontextmanager

from app.migracoes import executar_migracoes
from app.roteadores import roteador
from kapitour_shared.configuracao import configuracoes
from kapitour_shared.core.app_factory import criar_aplicacao


@asynccontextmanager
async def lifespan(_):
    executar_migracoes()
    yield


configuracoes.service_name = "engagement"

app = criar_aplicacao(
    titulo="Kapitour Engagement Service",
    versao="2.0.0",
    lifespan=lifespan,
    descricao="Favoritos, avaliações e engajamento do usuário.",
)

app.include_router(roteador, prefix="/api")
