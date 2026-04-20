# 🚀 DevConnect — LinkedIn Backend-Anwendung

> Ein LinkedIn-Klon als vollständige Fullstack-Anwendung.  
> **Backend:** FastAPI · PostgreSQL · Redis · Celery  
> **Frontend:** HTML : CSS : JS

---

## 👨‍💻 Über das Projekt

Dieses Projekt ist eine **vollständige Fullstack-Anwendung**, die im Rahmen der Vorbereitung auf eine **Ausbildung zum Fachinformatiker für Anwendungsentwicklung** in Deutschland entwickelt wird.

Das Ziel ist es, potenziellen Ausbildungsbetrieben zu zeigen, dass ich in der Lage bin, **echte, produktionsreife Anwendungen** von Grund auf zu bauen — sowohl Backend als auch Frontend.

**Was diese Anwendung kann:**
- Entwicklerprofile erstellen und verwalten
- Stellenangebote veröffentlichen und bewerben
- Verbindungen zwischen Nutzern aufbauen (wie LinkedIn)
- Skill-basierte Job- und Personenempfehlungen
- Echtzeit-Benachrichtigungen

**Inspiration:** LinkedIn — aber für Entwickler, mit offenem Quellcode und sauberer Architektur.

> 🎯 Das Projekt wird Schritt für Schritt aufgebaut — von Null bis Deployment.

---

## 🏗️ Architektur

```
devconnect/
├── backend/    → REST API (FastAPI)
└── frontend/   → Web-App (HTML;CSS;JS)
```

Die beiden Teile sind vollständig getrennt und kommunizieren über eine REST API.

---

## 📦 Tech Stack

### Backend
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

### Frontend
| Ebene | Technologie |
|-------|-------------|
| Framework | React 18 |
| Sprache | TypeScript |
| Styling | Tailwind CSS |
| HTTP Client | Axios |
| State Management | Zustand |
| Routing | React Router v6 |

---

## 🗂️ Projektstruktur

```
devconnect/
│
├── backend/
│   ├── app/
│   │   ├── auth/              # JWT, Login, Registrierung
│   │   ├── users/             # Benutzer-Modell & Endpunkte
│   │   ├── profiles/          # Profil, Skills, Erfahrung
│   │   ├── connections/       # Verbindungen & Empfehlungen
│   │   ├── jobs/              # Stellenangebote & Suche
│   │   ├── applications/      # Bewerbungen & Status
│   │   ├── notifications/     # Benachrichtigungen (Celery)
│   │   └── core/              # Config, DB, Redis, Celery
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── pages/             # Login, Register, Feed, Profil, Jobs
    │   ├── components/        # UI-Komponenten
    │   ├── api/               # API-Aufrufe (Axios)
    │   ├── store/             # Zustand (State Management)
    │   └── types/             # TypeScript-Typen
    ├── public/
    └── package.json
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
    skills      TEXT[],
    experience  JSONB,
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Verbindungen
CREATE TABLE connections (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID REFERENCES users(id) ON DELETE CASCADE,
    receiver_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    status       VARCHAR(20) DEFAULT 'pending',
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
    search_vector   TSVECTOR
);

-- Bewerbungen
CREATE TABLE applications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id     UUID REFERENCES jobs(id) ON DELETE CASCADE,
    status     VARCHAR(20) DEFAULT 'pending',
    cover_note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, job_id)
);

-- Benachrichtigungen
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    type       VARCHAR(50),
    payload    JSONB,
    is_read    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API-Endpunkte

### Authentifizierung
```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
```

### Benutzer & Profile
```
GET    /users/me
PATCH  /users/me
GET    /users/{id}
GET    /users/suggestions

GET    /users/me/profile
PATCH  /users/me/profile
POST   /users/me/avatar
```

### Verbindungen
```
POST   /connections/request/{user_id}
PATCH  /connections/{id}/accept
PATCH  /connections/{id}/reject
DELETE /connections/{id}
GET    /connections/my
GET    /connections/pending
```

### Stellenangebote
```
POST   /jobs
GET    /jobs
GET    /jobs/recommended
GET    /jobs/{id}
PATCH  /jobs/{id}
DELETE /jobs/{id}
```

### Bewerbungen
```
POST   /jobs/{id}/apply
GET    /applications/my
GET    /jobs/{id}/applications
PATCH  /applications/{id}/status
```

### Benachrichtigungen
```
GET    /notifications
PATCH  /notifications/{id}/read
PATCH  /notifications/read-all
```

---

## ⚙️ Quickstart

### Backend starten

```bash
cd backend
cp .env.example .env
docker-compose up --build
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Migrationen anwenden

```bash
docker-compose exec api alembic upgrade head
```

### Frontend starten *(kommt bald)*

```bash
cd frontend
npm install
npm run dev
```

Web-App: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

---

## 🗺️ Roadmap

### ✅ Backend
- [x] Authentifizierung (JWT + Refresh Tokens)
- [x] Benutzer & Profile
- [x] Stellenangebote + Volltextsuche
- [x] Bewerbungen
- [x] Verbindungen + Empfehlungen
- [x] Benachrichtigungen (Celery + Redis)
- [ ] WebSocket-Chat
- [ ] ElasticSearch für die Suche

### 🔜 Frontend
- [ ] Login & Registrierung
- [ ] Profil-Seite
- [ ] Jobs Feed
- [ ] Bewerbungen
- [ ] Verbindungen
- [ ] Benachrichtigungen
- [ ] Responsive Design

### 🚀 Deployment
- [ ] Backend → Railway / Render
- [ ] Frontend → Vercel
- [ ] CI/CD mit GitHub Actions

---

## 📝 Lizenz

MIT
