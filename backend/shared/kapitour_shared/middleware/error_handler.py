import logging
from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("kapitour.errors")


class MiddlewareTratamentoErros(BaseHTTPMiddleware):
    """Captura exceções não tratadas e retorna resposta JSON padronizada."""

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", None)
            logger.exception(
                "unhandled_error",
                extra={"request_id": request_id, "path": request.url.path},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Erro interno do servidor.",
                    "request_id": request_id,
                },
            )
