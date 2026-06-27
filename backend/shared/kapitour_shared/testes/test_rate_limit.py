"""Testes do rate limiting por rota."""

from kapitour_shared.configuracao import configuracoes
from kapitour_shared.middleware.rate_limit import _parse_limite, resolver_limite


class TestParseLimite:
    def test_minute(self):
        assert _parse_limite("5/minute") == (5, 60)

    def test_second(self):
        assert _parse_limite("10/second") == (10, 1)


class TestResolverLimite:
    def test_login(self):
        assert resolver_limite("/api/auth/login") == configuracoes.rate_limit_login

    def test_register(self):
        assert resolver_limite("/api/auth/register") == configuracoes.rate_limit_register

    def test_forgot_password(self):
        assert resolver_limite("/api/auth/forgot-password") == configuracoes.rate_limit_forgot_password

    def test_refresh(self):
        assert resolver_limite("/api/auth/refresh") == configuracoes.rate_limit_refresh

    def test_checkin(self):
        assert resolver_limite("/api/kapipass/checkin") == configuracoes.rate_limit_checkin

    def test_resgate_cupom(self):
        assert resolver_limite("/api/cupons/resgatar") == configuracoes.rate_limit_resgate_cupom

    def test_rota_generica(self):
        assert resolver_limite("/api/produtos") == configuracoes.rate_limit_default
