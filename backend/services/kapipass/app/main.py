from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.migracoes import executar_migracoes, semear_dados_iniciais
from app.roteadores import roteador
from kapitour_shared.banco_dados import FabricaSessao
from kapitour_shared.configuracao import configuracoes


@asynccontextmanager
async def lifespan(_: FastAPI):
    executar_migracoes()
    sessao = FabricaSessao()
    try:
        semear_dados_iniciais(sessao)
    finally:
        sessao.close()
    yield


app = FastAPI(title="Kapitour KapiPass Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.cors_origins.split(",") if configuracoes.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roteador, prefix="/api")
