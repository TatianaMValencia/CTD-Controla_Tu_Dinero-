#!/bin/sh
set -e
echo ">> alembic upgrade head (reintentos para Aiven/red)"
for i in 1 2 3 4 5; do
  if alembic upgrade head; then
    break
  fi
  echo ">> reintento $i/5 en 5s..."
  sleep 5
  if [ "$i" = "5" ]; then
    echo ">> no se pudo migrar la DB (revisa DATABASE_URL/Aiven)"; exit 1
  fi
done
echo ">> uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
