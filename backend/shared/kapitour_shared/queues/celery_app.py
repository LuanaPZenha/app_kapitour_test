import os

from celery import Celery

from kapitour_shared.configuracao import configuracoes

celery_app = Celery(
    "kapitour",
    broker=configuracoes.celery_broker_url,
    backend=configuracoes.celery_result_backend,
    include=["kapitour_shared.workers.tasks"],
)

_eager = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_always_eager=_eager,
    task_eager_propagates=_eager,
)
