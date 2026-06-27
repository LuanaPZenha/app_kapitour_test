"""Testes do ServicoEmail."""

from kapitour_shared.email.servico_email import ServicoEmail


class TestServicoEmail:
    def test_enviar_em_modo_dev_loga(self, monkeypatch):
        monkeypatch.setattr("kapitour_shared.configuracao.configuracoes.smtp_host", "")
        resultado = ServicoEmail().enviar("a@b.com", "Assunto", "<p>oi</p>")
        assert resultado["status"] == "logged"
        assert resultado["destinatario"] == "a@b.com"
