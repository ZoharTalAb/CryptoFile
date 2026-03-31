#!/bin/sh
set -e

echo "==> Preparing uploads directory..."
mkdir -p /app/uploads
chmod -R 777 /app/uploads
chown -R app:app /app/uploads

echo "==> Running database migrations..."
cd /app
RUNNING_MIGRATIONS=true gosu app alembic -c /app/alembic.ini upgrade head

echo "==> Starting API server..."
cd /app/src
exec gosu app uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info