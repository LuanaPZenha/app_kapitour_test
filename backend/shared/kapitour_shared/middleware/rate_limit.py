import logging
from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from kapitour_shared.autenticacao import decodificar_token
from kapitour_shared.cache.redis_client import obter_cliente_redis
from kapitour_shared.configuracao import configuracoes

logger = logging.getLogger("kapitour.ratelimit")


def _parse_limite(limite: str) -> tuple[int, int]:
    """Converte '5/minute' em (max_requests, window_seconds)."""
    partes = limite.split("/")
    max_req = int(partes[0])
    unidade = partes[1] if len(partes) > 1 else "minute"
    janela = {"second": 1, "minute": 60, "hour": 3600}.get(unidade, 60)
    return max_req, janela


class MiddlewareRateLimit(BaseHTTPMiddleware):
    """Rate limiting por IP e por usuário autenticado via Redis."""

    ROTAS_ESPECIAIS = {
        "/api/auth/login": "login",
        "/api/auth/register": "register",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        redis = obter_cliente_redis()
        if not redis:
            return await call_next(request)

        path = request.url.path
        limite_str = configuracoes.rate_limit_default
        for rota, tipo in self.ROTAS_ESPECIAIS.items():
            if path.endswith(rota) or path == rota:
                limite_str = (
                    configuracoes.rate_limit_login
                    if tipo == "login"
                    else configuracoes.rate_limit_register
                )
                break

        max_req, janela = _parse_limite(limite_str)
        ip = request.client.host if request.client else "unknown"
        chaves = [f"rl:ip:{ip}:{path}"]

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            payload = decodificar_token(auth.replace("Bearer ", "", 1))
            if payload and payload.get("sub"):
                chaves.append(f"rl:user:{payload['sub']}:{path}")

        for chave in chaves:
            atual = redis.incr(chave)
            if atual == 1:
                redis.expire(chave, janela)
            if atual > max_req:
                logger.warning("Rate limit excedido: %s", chave)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas requisições. Tente novamente em breve."},
                )

        return await call_next(request)
