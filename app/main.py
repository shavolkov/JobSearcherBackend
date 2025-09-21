from fastapi import FastAPI, Response
from sqlalchemy import text
from app.db.session import engine
from app.api.routers import jobs
app = FastAPI()



# Routers
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Health endpoints
@app.get("/healthz")
def healthz():
     return {"status": "ok"}

@app.get("/readyz")
def readyz():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return Response(f"not ready: {e}", media_type="text/plain", status_code=503)

@app.get("/test")
def test():
    # DB ping will be added after we wire up SQLAlchemy
    return {"TESTING": "TRUE"}