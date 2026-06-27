"""Testes do serviço de cache."""

from unittest.mock import MagicMock, patch

import pytest

from kapitour_shared.cache.cache_service import ServicoCache


class TestServicoCache:
    def test_obter_ou_carregar_sem_redis(self):
        cache = ServicoCache(prefixo="test")
        with patch.object(cache, "_redis", None):
            valor = cache.obter_ou_carregar("chave", lambda: {"ok": True})
        assert valor == {"ok": True}

    def test_obter_ou_carregar_com_cache_hit(self):
        cache = ServicoCache(prefixo="test")
        redis_fake = MagicMock()
        redis_fake.get.return_value = 'json:{"cached": true}'
        cache._redis = redis_fake
        valor = cache.obter_ou_carregar("chave", lambda: {"ok": False})
        assert valor == {"cached": True}
        redis_fake.get.assert_called_once()

    def test_definir_e_invalidar(self):
        cache = ServicoCache(prefixo="test")
        redis_fake = MagicMock()
        cache._redis = redis_fake
        cache.definir("item:1", {"a": 1}, ttl=60)
        redis_fake.setex.assert_called_once()
        cache.invalidar("item:1")
        redis_fake.delete.assert_called()
