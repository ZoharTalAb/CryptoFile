#!/bin/sh
set -e

echo "==> Preparing uploads directory..."
mkdir -p /app/uploads
chmod -R 777 /app/uploads
chown -R app:app /app/uploads

echo "==> Running database migrations..."
cd /app
RUNNING_MIGRATIONS=true gosu app alembic -c /app/alembic.ini upgrade head

echo "==> Verifying app import..."
cd /app/src
gosu app python - <<'PY'
import traceback
try:
    import main
    print("APP_IMPORT_OK")
except Exception:
    print("APP_IMPORT_FAILED")
    traceback.print_exc()
    raise
PY

echo "==> Starting API server..."
exec gosu app python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level debug