# 🚀 DevConnect — LinkedIn Fullstack-Anwendung

> Ein LinkedIn-Klon als vollständige Anwendung mit REST API und HTML/CSS/JS Frontend.  
> **Backend:** FastAPI · PostgreSQL · Redis · Celery  
> **Frontend:** Vanilla HTML · CSS · JavaScript (kein Framework)

---

## 👨‍💻 Über das Projekt

Dieses Projekt ist eine **vollständige Webanwendung**, die im Rahmen der Vorbereitung auf eine **Ausbildung zum Fachinformatiker für Anwendungsentwicklung** in Deutschland entwickelt wird.

Das Ziel ist es, potenziellen Ausbildungsbetrieben zu zeigen, dass ich in der Lage bin, **echte, produktionsreife Backend-Systeme** zu bauen:

- Durchdachte Architektur (kein reiner CRUD-Code)
- Asynchroner Stack (FastAPI + async SQLAlchemy)
- JWT-Authentifizierung mit Refresh-Token-Rotation
- Hintergrundaufgaben (Celery + Redis)
- PostgreSQL Volltextsuche mit tsvector + GIN-Index
- Containerisierung mit Docker
- CI/CD mit GitHub Actions
- Deployment auf Railway

**Inspiration:** LinkedIn — aber für Entwickler, mit offenem Quellcode und sauberer Architektur.

---

## 🌐 Live Demo

| | URL |
|---|---|
| 🖥️ Frontend | `https://deine-app.railway.app/` |
| 📡 API Docs | `https://deine-app.railway.app/docs` |
| ❤️ Health | `https://deine-app.railway.app/health` |

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
| | |
|---|---|
| Technologie | Vanilla HTML + CSS + JavaScript |
| Kein Framework | Bewusste Entscheidung — zeigt Grundlagenkenntnisse |
| API-Kommunikation | Fetch API mit Bearer Token |

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
│   ├── static/
│   │   └── index.html         # Frontend (HTML/CSS/JS)
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── pyproject.toml
│
└── .github/
    └── workflows/
        ├── ci.yml             # Tests bei jedem Push
        └── cd.yml             # Deployment auf Railway
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
GET    /users/me/profile
PATCH  /users/me/profile
```

### Verbindungen
```
POST   /connections/request/{user_id}
PATCH  /connections/{id}/accept
PATCH  /connections/{id}/reject
DELETE /connections/{id}
GET    /connections/my
GET    /connections/pending
GET    /connections/suggestions
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
GET    /notifications/unread-count
PATCH  /notifications/{id}/read
PATCH  /notifications/read-all
```

---

## ⚙️ Quickstart

```bash
git clone https://github.com/bagdanchik007/linkedin-fullstack.git
cd linkedin-fullstack/backend
cp .env.example .env
docker-compose up --build
```

Migrationen anwenden:
```bash
docker-compose exec api alembic upgrade head
```

Öffne [http://localhost:8000](http://localhost:8000) → Frontend  
Öffne [http://localhost:8000/docs](http://localhost:8000/docs) → Swagger UI

---

## 🧪 Tests

```bash
docker-compose exec api pytest tests/ -v
```

---

## 🗺️ Roadmap

### ✅ Backend
- [x] Authentifizierung (JWT + Refresh Tokens + Rotation)
- [x] Benutzer & Profile (Skills, Erfahrung, JSONB)
- [x] Stellenangebote + PostgreSQL Volltextsuche
- [x] Bewerbungen mit Statusverwaltung
- [x] Verbindungen + Skill-basierte Empfehlungen
- [x] Benachrichtigungen (Celery + Redis)
- [x] Tests (Pytest + SQLite In-Memory)
- [x] Docker + CI/CD (GitHub Actions)
- [x] Deployment (Railway)

### ✅ Frontend
- [x] HTML/CSS/JS Single-Page Interface
- [x] Login & Registrierung
- [x] Stellenangebote mit Suche
- [x] Dashboard mit Statistiken
- [x] API Health Check

---

## 📝 Lizenz

MIT
