FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# system pkgs (optional, helpful for psycopg if not binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# copy app last for better layer caching
COPY . /app

# entrypoint will run migrations then start Granian
CMD ["/app/entrypoint.sh"]
