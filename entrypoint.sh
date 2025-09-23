#!/bin/sh
set -eu

echo ">>> entrypoint starting"

# 1) Resolve DATABASE_URL (prod) or fall back to local dev
# Order: explicit DATABASE_URL -> Secrets Manager -> PGDATABASE_URL -> dev default
if [ -n "${DATABASE_URL:-}" ]; then
  URL="$DATABASE_URL"
else
  if [ -n "${DB_SECRET_ID:-}" ]; then
    # Build URL from Secrets Manager (needs boto3 in image & instance role on EC2)
    URL="$(python - <<'PY'
import os, json, urllib.parse, boto3
region = os.getenv("AWS_REGION", "us-east-2")
sid    = os.environ["DB_SECRET_ID"]  # name or ARN
sm = boto3.client("secretsmanager", region_name=region)
s  = json.loads(sm.get_secret_value(SecretId=sid)["SecretString"])

user = urllib.parse.quote_plus(s.get("username",""))
pwd  = urllib.parse.quote_plus(s.get("password",""))

# RDS-managed secret may not include host/port/dbname; allow env fallbacks
host = s.get("host") or os.getenv("DB_HOST")
port = str(s.get("port") or os.getenv("DB_PORT","5432"))
db   = s.get("dbname") or os.getenv("DB_NAME","postgres")

if not (user and pwd and host):
    raise SystemExit("Missing DB fields (need user/password/host). Provide DB_HOST/DB_NAME envs or use a 5-field secret.")

url = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"
if "sslmode=" not in url:
    url += "?sslmode=require"
print(url)
PY
)"
  else
    URL="${PGDATABASE_URL:-postgresql+psycopg://postgres:postgres@db:5432/postgres}"
  fi
fi

# Export for alembic/app
export DATABASE_URL="$URL"

# psycopg.connect() doesn't understand the "+psycopg" driver segment; normalize for the readiness probe
READY_URL="$(printf "%s" "$DATABASE_URL" | sed 's/postgresql+psycopg:\/\//postgresql:\/\//')"
export READY_URL    # <-- add this line
echo ">>> waiting for database ..."
python - <<'PY'
import os, time
import psycopg
url = os.environ["READY_URL"]
for i in range(60):
    try:
        with psycopg.connect(url, connect_timeout=3, autocommit=True):
            break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not ready after 60s")
PY

echo ">>> running alembic migrations ..."
# alembic upgrade head

echo ">>> launching server ..."
# Pick ONE: granian or uvicorn (granian per your requirements)
exec granian --interface asgi --host 0.0.0.0 --port 8000 app.main:app
# exec uvicorn app.main:app --host 0.0.0.0 --port 8000
