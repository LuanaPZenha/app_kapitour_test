import logging
import smtplib
from email.mime.text import MIMEText

from kapitour_shared.configuracao import configuracoes

logger = logging.getLogger("kapitour.email")


class ServicoEmail:
    """Envio de e-mails via SMTP ou log em desenvolvimento."""

    def enviar(self, destinatario: str, assunto: str, corpo_html: str) -> dict:
        if not configuracoes.smtp_host:
            logger.info(
                "Email (dev): to=%s subject=%s",
                destinatario,
                assunto,
            )
            return {"status": "logged", "destinatario": destinatario}

        msg = MIMEText(corpo_html, "html", "utf-8")
        msg["Subject"] = assunto
        msg["From"] = configuracoes.email_from
        msg["To"] = destinatario

        with smtplib.SMTP(configuracoes.smtp_host, configuracoes.smtp_port, timeout=30) as server:
            server.starttls()
            if configuracoes.smtp_user:
                server.login(configuracoes.smtp_user, configuracoes.smtp_password)
            server.send_message(msg)

        return {"status": "sent", "destinatario": destinatario}


servico_email = ServicoEmail()
