#!/usr/bin/env bash
echo ">>> SETTING env"
set -e

echo ">>> Starting entrypoint"

# Wait for the database to accept connections (simple loop)


python - <<'PY'
import os, time
import psycopg
url = os.getenv("PGDATABASE_URL", "postgresql://postgres:postgres@db:5432/app")
print("This is the database url: " + url)
for i in range(60):
    try:
        print("This is the database url: " +url)
        with psycopg.connect(url, connect_timeout=3) as _:
            # cur.execute("SELECT 1")
            # print("✅ psycopg OK:", cur.fetchone())
            break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not ready after 60s")
PY

# Apply migrations
echo ">>> Running migrations..."
alembic upgrade head

# Start the ASGI server
echo ">>> Launching Granian..."
exec granian --interface asgi --host 0.0.0.0 --port 8000 app.main:app
