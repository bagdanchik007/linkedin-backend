# 🚀 Linkedin - FullStack Andwendungsprogramm Frontend + Backend 

> Ein LinkedIn-Klon für Entwickler. Plattform für Networking, Jobsuche und Bewerbungen.  
> Gebaut mit FastAPI, PostgreSQL, Redis und Celery.

---

## 👨‍💻 Über das Projekt

Dieses Projekt ist ein **persönliches Lernprojekt**, das im Rahmen der Vorbereitung auf eine **Ausbildung zum Fachinformatiker für Anwendungsentwicklung** in Deutschland entstanden ist.

Das Ziel ist es, potenziellen Ausbildungsbetrieben nicht nur Syntaxkenntnisse zu zeigen, sondern die Fähigkeit, **echte Backend-Systeme** zu bauen:

- Durchdachte Architektur (kein reiner CRUD-Code)
- Asynchroner Stack (FastAPI + async SQLAlchemy)
- Hintergrundaufgaben (Celery + Redis)
- JWT-Authentifizierung mit Refresh-Tokens
- Geschäftslogik: Verbindungen, Bewerbungen, Empfehlungen

**Inspiration:** LinkedIn — aber für Entwickler, mit offenem Quellcode und sauberer Architektur.

> 🎯 Das Projekt wird nach einem 28-Tage-Plan aufgebaut — von Null bis Deployment.

---

## 📦 Tech Stack

| Ebene | Technologie |
|-------|-------------|
| Framework | FastAPI |
| Datenbank | PostgreSQL + SQLAlchemy (async) |
| Migrationen | Alembic |
| Cache / Queue | Redis |
| Hintergrundaufgaben | Celery |
| Authentifizierung | JWT (Access + Refresh Tokens) |
| Containerisierung | Docker + Docker Compose |
| Tests | Pytest + HTTPX |

---

## 🗂️ Projektstruktur

```
backend/
├── app/
│   ├── auth/
│   │   ├── router.py          # /auth/register, /auth/login, /auth/refresh, /auth/logout
│   │   ├── service.py         # JWT-Logik, Passwort-Hashing
│   │   ├── schemas.py         # Pydantic-Modelle
│   │   └── dependencies.py    # get_current_user
│   │
│   ├── users/
│   │   ├── router.py          # /users/me, /users/{id}, /users/suggestions
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py          # User-Modell
│   │
│   ├── profiles/
│   │   ├── router.py          # /users/me/profile
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py          # Profil-Modell (Bio, Skills, Standort)
│   │
│   ├── connections/
│   │   ├── router.py          # /connections/request, /accept, /reject, /my, /pending
│   │   ├── service.py         # Verbindungslogik + Empfehlungen
│   │   ├── schemas.py
│   │   └── models.py          # Verbindungs-Modell (Anfragender, Empfänger, Status)
│   │
│   ├── jobs/
│   │   ├── router.py          # /jobs CRUD + Suche + /jobs/recommended
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py          # Job-Modell
│   │
│   ├── applications/
│   │   ├── router.py          # /jobs/{id}/apply, /applications/my
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── models.py          # Bewerbungs-Modell (pending/accepted/rejected)
│   │
│   ├── notifications/
│   │   ├── router.py          # /notifications, /notifications/{id}/read
│   │   ├── service.py
│   │   ├── schemas.py
│   │   ├── models.py          # Benachrichtigungs-Modell
│   │   └── tasks.py           # Celery-Aufgaben
│   │
│   └── core/
│       ├── config.py          # Einstellungen (pydantic-settings)
│       ├── database.py        # Async SQLAlchemy Engine + Session
│       ├── redis.py           # Redis-Verbindung
│       └── celery_app.py      # Celery-Instanz
│
├── migrations/
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_jobs.py
│   ├── test_connections.py
│   └── test_applications.py
│
├── .env.example
├── .env
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── pyproject.toml
└── README.md
```

---

## 🧱 Datenbankschema

```sql
-- Benutzer
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(20) DEFAULT 'user',  -- 'user' | 'recruiter'
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Refresh Tokens
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    token       TEXT NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Profile
CREATE TABLE profiles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name   VARCHAR(255),
    bio         TEXT,
    location    VARCHAR(255),
    avatar_url  TEXT,
    skills      TEXT[],           -- PostgreSQL-Array
    experience  JSONB,            -- [{title, company, years}]
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Verbindungen
CREATE TABLE connections (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID REFERENCES users(id) ON DELETE CASCADE,
    receiver_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    status       VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'accepted' | 'rejected'
    created_at   TIMESTAMP DEFAULT NOW(),
    UNIQUE (requester_id, receiver_id)
);

-- Stellenangebote
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    company         VARCHAR(255),
    location        VARCHAR(255),
    skills_required TEXT[],
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    search_vector   TSVECTOR   -- Volltextsuche
);
CREATE INDEX jobs_search_idx ON jobs USING GIN(search_vector);

-- Bewerbungen
CREATE TABLE applications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id     UUID REFERENCES jobs(id) ON DELETE CASCADE,
    status     VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'accepted' | 'rejected'
    cover_note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, job_id)
);

-- Benachrichtigungen
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    type       VARCHAR(50),   -- 'connection_request' | 'application_update' | 'new_job'
    payload    JSONB,
    is_read    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API-Endpunkte

### Authentifizierung
```
POST   /auth/register          # Registrierung
POST   /auth/login             # Anmeldung → Access + Refresh Token
POST   /auth/refresh           # Access Token erneuern
POST   /auth/logout            # Refresh Token widerrufen
```

### Benutzer & Profile
```
GET    /users/me               # Aktueller Benutzer
PATCH  /users/me               # Daten aktualisieren
GET    /users/{id}             # Öffentliches Profil
GET    /users/suggestions      # Personenempfehlungen

GET    /users/me/profile       # Eigenes Profil
PATCH  /users/me/profile       # Profil aktualisieren
POST   /users/me/avatar        # Avatar hochladen
```

### Verbindungen
```
POST   /connections/request/{user_id}   # Anfrage senden
PATCH  /connections/{id}/accept         # Annehmen
PATCH  /connections/{id}/reject         # Ablehnen
DELETE /connections/{id}                # Kontakt entfernen
GET    /connections/my                  # Meine Kontakte
GET    /connections/pending             # Eingehende Anfragen
```

### Stellenangebote
```
POST   /jobs                   # Stelle erstellen (nur Recruiter)
GET    /jobs                   # Liste (Filter: skills, company, location)
GET    /jobs/recommended       # Empfehlungen nach Profil-Skills
GET    /jobs/{id}              # Stellendetails
PATCH  /jobs/{id}              # Bearbeiten (nur Autor)
DELETE /jobs/{id}              # Löschen (nur Autor)
```

### Bewerbungen
```
POST   /jobs/{id}/apply                  # Bewerben
GET    /applications/my                  # Meine Bewerbungen
GET    /jobs/{id}/applications           # Bewerbungen zur Stelle (Recruiter)
PATCH  /applications/{id}/status         # Status ändern (Recruiter)
```

### Benachrichtigungen
```
GET    /notifications                    # Liste der Benachrichtigungen
PATCH  /notifications/{id}/read          # Als gelesen markieren
PATCH  /notifications/read-all           # Alle als gelesen markieren
```

---

## ⚙️ Quickstart

### 1. Repository klonen und Umgebung einrichten

```bash
git clone https://github.com/yourname/devconnect-backend
cd devconnect-backend
cp .env.example .env
```

### 2. `.env` ausfüllen

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/devconnect
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### 3. Mit Docker starten

```bash
docker-compose up -d
```

### 4. Migrationen anwenden

```bash
alembic upgrade head
```

### 5. Server starten

```bash
uvicorn app.main:app --reload
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

---

## 🐳 Docker Compose

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: devconnect
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.core.celery_app worker --loglevel=info
    env_file: .env
    depends_on:
      - redis

volumes:
  pgdata:
```

---

## 🗺️ Roadmap

- [x] Authentifizierung (JWT + Refresh Tokens)
- [x] Benutzer & Profile
- [x] Stellenangebote + Volltextsuche
- [x] Bewerbungen
- [x] Verbindungen + Empfehlungen
- [x] Benachrichtigungen (Celery + Redis)
- [ ] WebSocket-Chat
- [ ] ElasticSearch für die Suche
- [ ] Feed (Beiträge + Likes)
- [ ] Deployment (Railway / Render)

---

## 📝 Lizenz

MIT
