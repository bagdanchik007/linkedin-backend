# ---- Stufe 1: Abhängigkeiten installieren ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Poetry installieren
RUN pip install poetry==1.8.2

# Nur pyproject.toml und lock-Datei kopieren — besseres Layer-Caching
COPY pyproject.toml poetry.lock* ./

# Abhängigkeiten in ein eigenes Verzeichnis installieren (kein venv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# ---- Stufe 2: Produktions-Image ----
FROM python:3.11-slim AS production

WORKDIR /app

# Installierte Pakete aus Builder-Stufe kopieren
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Quellcode kopieren
COPY . .

# Nicht-root-Benutzer für mehr Sicherheit
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Port freigeben
EXPOSE 8000

# Produktionsserver ohne --reload starten
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
