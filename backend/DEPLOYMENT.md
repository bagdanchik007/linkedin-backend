# 🚀 Deployment-Anleitung

## Railway (empfohlen)

### Voraussetzungen
- Konto auf [railway.app](https://railway.app)
- Railway CLI: `npm install -g @railway/cli`

### Schritt 1 — Railway Projekt erstellen

```bash
cd backend
railway login
railway init
```

### Schritt 2 — PostgreSQL hinzufügen

Im Railway Dashboard:
1. **New Service** → **Database** → **PostgreSQL**
2. `DATABASE_URL` wird automatisch als Umgebungsvariable gesetzt

### Schritt 3 — Redis hinzufügen

Im Railway Dashboard:
1. **New Service** → **Database** → **Redis**
2. `REDIS_URL` wird automatisch gesetzt

### Schritt 4 — Umgebungsvariablen setzen

Im Railway Dashboard unter **Variables**:

```
SECRET_KEY=sehr-langer-zufaelliger-schluessel-mindestens-32-zeichen
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### Schritt 5 — Deployen

```bash
cd backend
railway up
```

### Schritt 6 — Migrationen ausführen

```bash
railway run alembic upgrade head
```

### Schritt 7 — API testen

```bash
# URL aus Railway Dashboard kopieren
curl https://deine-app.railway.app/health
```

---

## GitHub Actions CI/CD einrichten

### Railway Token holen

1. Railway Dashboard → **Account Settings** → **Tokens**
2. Token kopieren

### Token in GitHub hinterlegen

1. GitHub Repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**:
   - Name: `RAILWAY_TOKEN`
   - Value: Dein Railway Token

### Automatisches Deployment

Ab jetzt wird bei jedem Push auf `main`:
1. CI läuft — Tests werden ausgeführt
2. CD läuft — automatisch auf Railway deployen

---

## Lokale Entwicklung

```bash
# Umgebung starten
docker-compose up --build

# Migrationen ausführen
docker-compose exec api alembic upgrade head

# Tests ausführen
docker-compose exec api pytest tests/ -v

# Logs anzeigen
docker-compose logs -f api
```

## Nützliche Befehle

```bash
# Neue Migration erstellen
docker-compose exec api alembic revision --autogenerate -m "beschreibung"

# Datenbankänderungen rückgängig machen
docker-compose exec api alembic downgrade -1

# Celery Worker Status
docker-compose exec celery celery -A app.core.celery_app inspect active
```
