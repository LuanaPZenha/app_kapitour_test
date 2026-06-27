"""Testes de sanitização de entradas."""

import pytest

from kapitour_shared.security.sanitization import (
    gerar_token_aleatorio,
    sanitizar_email,
    sanitizar_texto,
    validar_senha_forte,
)


class TestSanitizacao:
    def test_sanitizar_texto_remove_html(self):
        assert sanitizar_texto("<script>alert(1)</script>oi") == "oi"

    def test_sanitizar_email_lowercase(self):
        assert sanitizar_email("  Test@Mail.COM ") == "test@mail.com"

    def test_validar_senha_forte_ok(self):
        assert validar_senha_forte("SenhaForte1") == []

    def test_validar_senha_fraca(self):
        erros = validar_senha_forte("abc")
        assert len(erros) >= 2

    def test_gerar_token_unico(self):
        assert gerar_token_aleatorio() != gerar_token_aleatorio()
