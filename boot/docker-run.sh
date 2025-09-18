#!/usr/bin/env bash
set -e  # exit immediately if a command fails

# Activate the venv
source /opt/venv/bin/activate

# Move to app directory
cd /code

# Default to 0.0.0.0:8000 unless overridden
RUN_PORT=${PORT:-8000}
RUN_HOST=${HOST:-0.0.0.0}

# Run app with Gunicorn + Uvicorn worker
exec gunicorn -k uvicorn.workers.UvicornWorker -b $RUN_HOST:$RUN_PORT main:app
