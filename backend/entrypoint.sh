#!/bin/sh
set -e

mkdir -p /app/uploads
chmod -R 777 /app/uploads
chown -R app:app /app/uploads

cd /app
gosu app alembic -c /app/alembic.ini upgrade head

cd /app/src
exec gosu app uvicorn main:app --host 0.0.0.0 --port 8000