import logging
from typing import Any

from kapitour_shared.queues.celery_app import celery_app

logger = logging.getLogger("kapitour.workers")


@celery_app.task(name="kapitour.enviar_email", bind=True, max_retries=3)
def enviar_email_assincrono(self, destinatario: str, assunto: str, corpo: str) -> dict:
    """Envia e-mail de forma assíncrona via ServicoEmail."""
    from kapitour_shared.email.servico_email import servico_email

    try:
        return servico_email.enviar(destinatario, assunto, corpo)
    except Exception as exc:
        logger.exception("Falha ao enviar e-mail para %s", destinatario)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="kapitour.processar_imagem")
def processar_imagem_assincrona(caminho: str, operacoes: list[str]) -> dict:
    logger.info("Processando imagem: %s ops=%s", caminho, operacoes)
    return {"status": "processed", "caminho": caminho}


@celery_app.task(name="kapitour.gerar_qrcode")
def gerar_qrcode_assincrono(dados: str, destino: str) -> dict:
    logger.info("Gerando QR Code: destino=%s", destino)
    return {"status": "generated", "destino": destino}


@celery_app.task(name="kapitour.gerar_kapipass")
def gerar_kapipass_assincrono(usuario_id: int) -> dict:
    logger.info("Gerando KapiPass para usuario_id=%s", usuario_id)
    return {"status": "generated", "usuario_id": usuario_id}


@celery_app.task(name="kapitour.notificacao_push")
def enviar_notificacao_push(usuario_id: int, titulo: str, mensagem: str) -> dict:
    logger.info("Push: user=%s title=%s", usuario_id, titulo)
    return {"status": "sent", "usuario_id": usuario_id}


@celery_app.task(name="kapitour.exportar_relatorio")
def exportar_relatorio_assincrono(tipo: str, parametros: dict) -> dict:
    logger.info("Exportando relatório: tipo=%s", tipo)
    return {"status": "exported", "tipo": tipo}


@celery_app.task(name="kapitour.registrar_log")
def registrar_log_assincrono(registro: dict[str, Any]) -> dict:
    logger.info("Log assíncrono: %s", registro.get("evento"))
    return {"status": "logged"}
