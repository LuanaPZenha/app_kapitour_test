import logging
import time
from collections.abc import Callable

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("kapitour.http")

REQUEST_COUNT = Counter(
    "kapitour_http_requests_total",
    "Total de requisições HTTP",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "kapitour_http_request_duration_seconds",
    "Latência das requisições HTTP",
    ["method", "path"],
)


class MiddlewareTempoResposta(BaseHTTPMiddleware):
    """Mede tempo de resposta e registra métricas Prometheus."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        inicio = time.perf_counter()
        response = await call_next(request)
        duracao = time.perf_counter() - inicio
        path = request.url.path
        method = request.method
        status = response.status_code

        REQUEST_LATENCY.labels(method=method, path=path).observe(duracao)
        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()

        request_id = getattr(request.state, "request_id", None)
        logger.info(
            "request_completed",
            extra={
                "method": method,
                "path": path,
                "status": status,
                "duration_ms": round(duracao * 1000, 2),
                "request_id": request_id,
                "client_ip": request.client.host if request.client else None,
            },
        )
        response.headers["X-Response-Time"] = f"{duracao * 1000:.2f}ms"
        return response
