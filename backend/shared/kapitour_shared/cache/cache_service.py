import base64
import json
import logging
import pickle
from typing import Any, Callable, TypeVar

from kapitour_shared.cache.redis_client import obter_cliente_redis
from kapitour_shared.configuracao import configuracoes

logger = logging.getLogger("kapitour.cache")
T = TypeVar("T")


class ServicoCache:
    """Cache-aside: Redis → função de origem → salvar no Redis."""

    def __init__(self, prefixo: str = "kapitour", ttl: int | None = None):
        self._prefixo = prefixo
        self._ttl = ttl or configuracoes.cache_default_ttl
        self._redis = obter_cliente_redis()

    def _chave(self, chave: str) -> str:
        return f"{self._prefixo}:{chave}"

    def _serializar(self, valor: Any) -> str:
        try:
            return "json:" + json.dumps(valor, default=str)
        except (TypeError, ValueError):
            return "pickle:" + base64.b64encode(pickle.dumps(valor)).decode("ascii")

    def _deserializar(self, bruto: str) -> Any:
        if bruto.startswith("json:"):
            return json.loads(bruto[5:])
        if bruto.startswith("pickle:"):
            return pickle.loads(base64.b64decode(bruto[7:].encode("ascii")))
        return json.loads(bruto)

    def obter(self, chave: str) -> Any | None:
        if not self._redis:
            return None
        try:
            valor = self._redis.get(self._chave(chave))
            return self._deserializar(valor) if valor else None
        except Exception as exc:
            logger.debug("Erro ao ler cache %s: %s", chave, exc)
            return None

    def definir(self, chave: str, valor: Any, ttl: int | None = None) -> None:
        if not self._redis:
            return
        try:
            self._redis.setex(
                self._chave(chave),
                ttl or self._ttl,
                self._serializar(valor),
            )
        except Exception as exc:
            logger.debug("Erro ao gravar cache %s: %s", chave, exc)

    def invalidar(self, chave: str) -> None:
        if not self._redis:
            return
        try:
            self._redis.delete(self._chave(chave))
        except Exception as exc:
            logger.debug("Erro ao invalidar cache %s: %s", chave, exc)

    def invalidar_padrao(self, padrao: str) -> None:
        """Invalida chaves que correspondem ao padrão (ex: pontos:*)."""
        if not self._redis:
            return
        try:
            chaves = self._redis.keys(self._chave(padrao))
            if chaves:
                self._redis.delete(*chaves)
        except Exception as exc:
            logger.debug("Erro ao invalidar padrão %s: %s", padrao, exc)

    def obter_ou_carregar(
        self,
        chave: str,
        carregar: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        cached = self.obter(chave)
        if cached is not None:
            return cached
        valor = carregar()
        if valor is not None:
            self.definir(chave, valor, ttl)
        return valor
