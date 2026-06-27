from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from kapitour_shared.configuracao import configuracoes
from kapitour_shared.core.health import registrar_rotas_monitoramento
from kapitour_shared.core.logging_config import configurar_logging
from kapitour_shared.middleware.error_handler import MiddlewareTratamentoErros
from kapitour_shared.middleware.rate_limit import MiddlewareRateLimit
from kapitour_shared.middleware.request_id import MiddlewareRequestId
from kapitour_shared.middleware.security_headers import MiddlewareHeadersSeguranca
from kapitour_shared.middleware.timing import MiddlewareTempoResposta


def criar_aplicacao(
    titulo: str,
    versao: str = "2.0.0",
    lifespan: Callable | None = None,
    descricao: str = "",
) -> FastAPI:
    """Factory centralizada — aplica middlewares de produção em todos os serviços."""
    configurar_logging(configuracoes.service_name)

    app = FastAPI(
        title=titulo,
        version=versao,
        description=descricao,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "health", "description": "Monitoramento e saúde do serviço"},
            {"name": "auth", "description": "Autenticação e autorização"},
            {"name": "usuarios", "description": "Gestão de perfis de usuário"},
            {"name": "conteudo", "description": "Pontos turísticos, categorias e rotas"},
            {"name": "engajamento", "description": "Favoritos e avaliações"},
            {"name": "commerce", "description": "Produtos e cupons"},
            {"name": "kapipass", "description": "Gamificação e check-ins"},
        ],
    )

    origens = (
        ["*"]
        if configuracoes.cors_origins == "*"
        else [o.strip() for o in configuracoes.cors_origins.split(",")]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(MiddlewareTratamentoErros)
    app.add_middleware(MiddlewareRateLimit)
    app.add_middleware(MiddlewareHeadersSeguranca)
    app.add_middleware(MiddlewareTempoResposta)
    app.add_middleware(MiddlewareRequestId)

    registrar_rotas_monitoramento(app)
    return app
