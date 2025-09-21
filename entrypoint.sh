#!/usr/bin/env sh
set -e

# Load environment
: "${DB_ENGINE:=sqlite}"
: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=medic_query}"
: "${DB_USER:=postgres}"
: "${DB_PASSWORD:=}"

if [ "$DB_ENGINE" = "postgres" ] ; then
  echo "[entrypoint] Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
  # Wait for PostgreSQL to be ready
  python - <<'PY'
import os, time, sys
import socket
host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', '5432'))
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print('[entrypoint] PostgreSQL is available')
            sys.exit(0)
    except OSError:
        print('[entrypoint] Waiting...')
        time.sleep(1)
print('[entrypoint] Timeout waiting for PostgreSQL', file=sys.stderr)
sys.exit(1)
PY
fi

# Apply migrations
python medic_query/medic_query/manage.py migrate --noinput

# Collect static files
python medic_query/medic_query/manage.py collectstatic --noinput

# Create default superuser if variables are present (optional)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "[entrypoint] Ensuring superuser exists..."
  python medic_query/medic_query/manage.py createsuperuser --noinput || true
fi

# Start Gunicorn
exec gunicorn medic_query.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile '-' \
    --error-logfile '-' \
    --timeout 120
