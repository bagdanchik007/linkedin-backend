# ---- Stufe 1: Abhängigkeiten installieren ----
FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install poetry==1.8.2

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# ---- Stufe 2: Produktions-Image ----
FROM python:3.11-slim AS production

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Nicht-root-Benutzer für mehr Sicherheit
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"