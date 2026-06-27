import logging
from datetime import datetime
from typing import Any

from kapitour_shared.cache.redis_client import obter_cliente_redis
from kapitour_shared.configuracao import configuracoes

logger = logging.getLogger("kapitour.audit")


def registrar_evento_auditoria(
    evento: str,
    usuario_id: int | None = None,
    auth_id: str | None = None,
    ip: str | None = None,
    detalhes: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> None:
    """Registra evento de auditoria em log estruturado e fila Redis."""
    registro = {
        "evento": evento,
        "usuario_id": usuario_id,
        "auth_id": auth_id,
        "ip": ip,
        "request_id": request_id,
        "detalhes": detalhes or {},
        "timestamp": datetime.utcnow().isoformat(),
        "service": configuracoes.service_name,
    }
    logger.info("audit_event", extra=registro)

    redis = obter_cliente_redis()
    if redis:
        try:
            chave = f"audit:{datetime.utcnow().strftime('%Y%m%d')}"
            redis.lpush(chave, str(registro))
            redis.expire(chave, 86400 * 30)
        except Exception:
            pass

    try:
        from kapitour_shared.workers.tasks import registrar_log_assincrono

        registrar_log_assincrono.delay(registro)
    except Exception:
        pass
