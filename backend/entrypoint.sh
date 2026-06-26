#!/bin/sh
set -e
python /app/scripts/ensure_microservice_data.py 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
