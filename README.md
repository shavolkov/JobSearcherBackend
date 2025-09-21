# FastAPI + Granian + Postgres (Docker) + SQLAlchemy 2.0 + Alembic

A minimal, pragmatic backend scaffold with:

- **FastAPI** app served by **Granian** (ASGI)  
- **Postgres** in its own container (persistent via a named volume)  
- **SQLAlchemy 2.0** ORM + session dependency  
- **Alembic** for migrations (autogenerate enabled)  
- Health probes: `/healthz` (liveness) and `/readyz` (DB ping)

## Quick start

```bash
# 1) Build + run (API + DB)
docker compose up --build

# 2) Hit liveness / readiness
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz

# 3) Create a job (simple JSON body)
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Job"}'

# 4) List jobs
curl http://127.0.0.1:8000/jobs
