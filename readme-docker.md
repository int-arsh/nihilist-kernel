# Docker Run Guide (Local + Prod)

This project has 2 services:
- `backend` (Flask + Gunicorn) on port `5000`
- `frontend` (Vite build served by Nginx) on port `3000`

---

## 1) Local Development Run (Docker Compose)

### Prerequisites
- Docker Engine + Compose plugin installed
- Port `3000` and `5000` free

### Step A: Create backend env file
Create this file:
- `bend/.env.dev`

Example:
```env
GOOGLE_API_KEY=your_dev_google_api_key
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step B: Start services
From project root:
```bash
docker compose up --build
```

### Step C: Access
- Frontend: http://localhost:3000
- Backend health: http://localhost:5000/health

### Step D: Stop
```bash
docker compose down
```

> Note: Do not use `docker compose down -v` if you want to keep SQLite volume data.

---

## 2) Local Prod-like Run (build with production API URL)

Use this when you want frontend image baked with production backend URL.

```bash
VITE_API_BASE_URL=https://your-backend-domain.com docker compose up --build
```

This value is used at frontend build time by:
- `fend/Dockerfile` via `ARG VITE_API_BASE_URL`

---

## 3) Production Run Strategy (Simple)

Recommended production behavior:
- Inject `GOOGLE_API_KEY` at runtime (never hardcode)
- Set `ALLOWED_ORIGINS` to real frontend domain
- Set `VITE_API_BASE_URL` to real backend domain during frontend image build

Example values:
```env
GOOGLE_API_KEY=***
ALLOWED_ORIGINS=https://your-frontend-domain.com
VITE_API_BASE_URL=https://your-backend-domain.com
```

---

## 4) Health + Restart (already configured)

In `docker-compose.yml`:
- `restart: unless-stopped`
- backend healthcheck uses `/health`
- frontend healthcheck checks Nginx root

Check state:
```bash
docker compose ps
```

---

## 5) Troubleshooting

### CORS error in browser
- Ensure backend `ALLOWED_ORIGINS` includes current frontend origin.

### API key missing / backend crash
- Ensure `GOOGLE_API_KEY` is present in `bend/.env.dev`.

### SQLite not persisting
- Ensure DB path is under mounted volume path (`/app/data`).
- Avoid `docker compose down -v`.

---

## 6) Security Basics

- Keep real env files out of git.
- Commit only example env files (`*.example`).
- Rotate keys if exposed in logs/chat/screenshots.
