import logging
import sys

from pythonjsonlogger import jsonlogger

from kapitour_shared.configuracao import configuracoes


def configurar_logging(nome_servico: str | None = None) -> logging.Logger:
    """Configura logging estruturado em JSON para produção."""
    servico = nome_servico or configuracoes.service_name
    logger = logging.getLogger("kapitour")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO if configuracoes.environment == "production" else logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger = logging.LoggerAdapter(logger, {"service": servico})
    return logger
