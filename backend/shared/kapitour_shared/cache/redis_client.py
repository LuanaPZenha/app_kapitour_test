import logging
from functools import lru_cache

import redis

from kapitour_shared.configuracao import configuracoes

logger = logging.getLogger("kapitour.redis")


def obter_cliente_redis() -> redis.Redis | None:
    """Retorna cliente Redis ou None se desabilitado/indisponível."""
    if not configuracoes.redis_enabled:
        return None
    return _conectar_redis()


@lru_cache(maxsize=1)
def _conectar_redis() -> redis.Redis | None:
    try:
        cliente = redis.from_url(
            configuracoes.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        cliente.ping()
        return cliente
    except (redis.RedisError, OSError) as exc:
        logger.warning("Redis indisponível, operando sem cache: %s", exc)
        return None


def redis_disponivel() -> bool:
    cliente = obter_cliente_redis()
    if not cliente:
        return False
    try:
        cliente.ping()
        return True
    except redis.RedisError:
        return False
