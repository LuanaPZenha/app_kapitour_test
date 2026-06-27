"""Configuração global de pytest — evita conflito backend/app vs services/*/app."""

import os
import sys
from pathlib import Path

# Testes rodam sem Redis/Celery externo por padrão
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")

BACKEND = Path(__file__).resolve().parent


def pytest_sessionstart(session):
    """Remove a raiz backend/ do sys.path para o monolito não sombrear `app`."""
    backend_str = str(BACKEND)
    while backend_str in sys.path:
        sys.path.remove(backend_str)
