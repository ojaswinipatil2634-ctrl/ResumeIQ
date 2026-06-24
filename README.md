# ResumeIQ — Full Stack Setup Guide

> *Your resume, intelligently understood.*

ResumeIQ is an AI-powered resume analysis platform. It scores your resume against ATS systems, matches it to job descriptions, prepares you for interviews, and maps out your career roadmap.

---

## Project Structure

```
resumeiq/
├── backend/          ← FastAPI (Python) — the API server
│   ├── app/
│   │   ├── api/      ← Route handlers (auth, resume, ats, job-match, …)
│   │   ├── core/     ← Config, JWT dependencies
│   │   ├── db/       ← SQLAlchemy engine & session
│   │   ├── models/   ← ORM table definitions
│   │   ├── schemas/  ← Pydantic request/response shapes
│   │   ├── services/ ← Business logic (analysis, scoring, …)
│   │   ├── utils/    ← PDF/DOCX extractor, skills dictionary, …
│   │   └── main.py   ← App factory & router registration
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/         ← React 18 + TypeScript + Tailwind CSS
    ├── src/
    │   ├── pages/    ← 13 pages (Landing, Dashboard, ATS, JobMatch, …)
    │   ├── components/
    │   ├── services/ ← Axios calls to every backend endpoint
    │   ├── contexts/ ← AuthContext, ResumeContext
    │   └── …
    ├── package.json
    └── .env
```

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | 9+ | Comes with Node.js |

---

## 1 — Backend Setup

### 1.1 Navigate to the backend folder

```bash
cd resumeiq/backend
```

### 1.2 Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 1.3 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 1.4 Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and update the `SECRET_KEY` — it must be a long random string:

```bash
# Generate a secure key (run this in your terminal):
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output as your `SECRET_KEY` in `.env`. The rest of the defaults work out of the box.

```env
APP_NAME=ResumeIQ
APP_VERSION=1.0.0
DEBUG=true

# SQLite — no database server needed
DATABASE_URL=sqlite:///./resumeiq.db

# CHANGE THIS!
SECRET_KEY=paste-your-generated-secret-here

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 1.5 Start the backend server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 1.6 Verify it's working

Open your browser and visit:

- **Swagger UI (API docs):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/api/v1/health

---

## 2 — Frontend Setup

Open a **new terminal tab/window** (keep the backend running).

### 2.1 Navigate to the frontend folder

```bash
cd resumeiq/frontend
```

### 2.2 Install Node.js dependencies

```bash
npm install
```

### 2.3 Check the `.env` file

The `.env` file is already pre-configured to point at your local backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

No changes needed for local development.

### 2.4 Start the frontend dev server

```bash
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 2.5 Open the app

Visit **http://localhost:5173** in your browser.

---

## 3 — Running Both Together

You need **two terminal windows** open simultaneously:

| Terminal | Command | URL |
|----------|---------|-----|
| Terminal 1 (backend) | `uvicorn app.main:app --reload --port 8000` | http://localhost:8000 |
| Terminal 2 (frontend) | `npm run dev` | http://localhost:5173 |

---

## 4 — First Steps in the App

1. Go to **http://localhost:5173**
2. Click **Get Started** → create a free account
3. Go to **Upload Resume** → drag and drop a PDF or DOCX resume
4. After upload you'll be automatically redirected to the **Analysis** page
5. Use the sidebar to navigate to **ATS Score**, **Job Match**, **Interview Prep**, and **Career Roadmap**

---

## 5 — API Endpoints Reference

All endpoints are prefixed with `http://localhost:8000`. Protected routes require:
```
Authorization: Bearer <access_token>
```

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ✗ | Create account |
| POST | `/api/auth/login` | ✗ | Login, receive JWT |
| GET | `/api/auth/me` | ✓ | Get current user |
| POST | `/api/resume/upload` | ✓ | Upload PDF/DOCX |
| GET | `/api/analysis/{id}` | ✓ | Full resume analysis |
| GET | `/api/ats/{id}` | ✓ | ATS score + section breakdown |
| POST | `/api/job-match/{id}` | ✓ | Match resume to job description |
| GET | `/api/improve/{id}` | ✓ | Improvement suggestions |
| GET | `/api/interview/{id}` | ✓ | Interview questions |
| GET | `/api/roadmap/{id}` | ✓ | Career roadmap |
| GET | `/api/dashboard/stats` | ✓ | Platform analytics |

Full interactive docs: **http://localhost:8000/docs**

---

## 6 — Tech Stack

### Backend
- **FastAPI** — web framework
- **SQLAlchemy** — ORM (SQLite by default, swap to PostgreSQL for production)
- **pypdf + python-docx** — PDF and DOCX text extraction
- **python-jose** — JWT token generation & validation
- **passlib[bcrypt]** — password hashing
- **pydantic-settings** — environment variable management

### Frontend
- **React 18 + TypeScript** — UI framework
- **Vite** — build tool & dev server
- **Tailwind CSS** — utility-first styling
- **Framer Motion** — animations (score ring, page transitions, stagger reveals)
- **Recharts** — analytics charts (area chart, horizontal bar chart)
- **Axios** — HTTP client with JWT interceptors
- **React Router v6** — client-side routing
- **Lucide React** — icons

---

## 7 — Troubleshooting

### "Module not found" on backend start
Make sure you activated your virtual environment (`source venv/bin/activate`) before running `pip install` and `uvicorn`.

### "Cannot connect to backend" / CORS errors
Ensure the backend is running on port **8000** and the frontend `.env` has `VITE_API_BASE_URL=http://localhost:8000`.

### "No text extracted" error on upload (422)
The uploaded file is likely a scanned image PDF with no embedded text. Try a text-based PDF or a DOCX file.

### SQLite database locked
Stop all running backend processes, then restart with `uvicorn app.main:app --reload --port 8000`.

### Frontend shows blank page after login
Open the browser console. If you see `401 Unauthorized`, your JWT may have expired (tokens last 30 minutes). Log out and log back in.

### Port already in use
```bash
# Kill whatever is on port 8000
lsof -ti:8000 | xargs kill -9

# Kill whatever is on port 5173
lsof -ti:5173 | xargs kill -9
```

---

## 8 — Production Notes

For deploying to production:

- Set `DEBUG=false` in `.env`
- Replace `SECRET_KEY` with a cryptographically secure random string
- Replace `DATABASE_URL` with a PostgreSQL connection string
- Set `VITE_API_BASE_URL` in the frontend `.env` to your actual backend domain
- Run the frontend build with `npm run build` and serve `dist/` with a static host (Vercel, Netlify, Nginx)
- Run the backend with a production ASGI server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Restrict CORS `allow_origins` in `app/main.py` to your actual frontend domain

---

*ResumeIQ v1.0 — Built with FastAPI + React*
