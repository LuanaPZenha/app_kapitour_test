from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from kapitour_shared.banco_dados import motor_banco
from kapitour_shared.cache.redis_client import redis_disponivel
from kapitour_shared.configuracao import configuracoes


def _verificar_banco() -> dict:
    try:
        with motor_banco.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def _verificar_redis() -> dict:
    if not configuracoes.redis_enabled:
        return {"status": "disabled"}
    ok = redis_disponivel()
    return {"status": "ok" if ok else "error"}


def _verificar_workers() -> dict:
    try:
        from kapitour_shared.queues.celery_app import celery_app

        insp = celery_app.control.inspect(timeout=1.0)
        ativos = insp.active() if insp else None
        if ativos is None:
            return {"status": "unknown", "detail": "Worker não respondeu"}
        return {"status": "ok", "workers": len(ativos)}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def registrar_rotas_monitoramento(app: FastAPI) -> None:
    @app.get("/api/health", tags=["health"], summary="Health check do serviço")
    def health():
        banco = _verificar_banco()
        redis = _verificar_redis()
        geral = "ok" if banco["status"] == "ok" else "degraded"
        return {
            "status": geral,
            "service": configuracoes.service_name,
            "checks": {"database": banco, "redis": redis},
        }

    @app.get("/api/status", tags=["health"], summary="Status detalhado do serviço")
    def status():
        return {
            "service": configuracoes.service_name,
            "environment": configuracoes.environment,
            "database": _verificar_banco(),
            "redis": _verificar_redis(),
            "workers": _verificar_workers(),
        }

    @app.get("/api/metrics", tags=["health"], summary="Métricas Prometheus")
    def metrics():
        return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
