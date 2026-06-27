"""Testes de workers Celery (modo eager)."""

from kapitour_shared.workers.tasks import (
    enviar_email_assincrono,
    gerar_qrcode_assincrono,
    registrar_log_assincrono,
)


class TestWorkers:
    def test_enviar_email_eager(self):
        resultado = enviar_email_assincrono("test@kapitour.com", "Teste", "<p>ok</p>")
        assert resultado["status"] in ("logged", "sent")

    def test_gerar_qrcode(self):
        resultado = gerar_qrcode_assincrono("dados", "/tmp/qr.png")
        assert resultado["status"] == "generated"

    def test_registrar_log(self):
        resultado = registrar_log_assincrono({"evento": "teste"})
        assert resultado["status"] == "logged"
