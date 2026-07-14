# Full Step-by-Step Guide — Running this in VS Code

This walks you through **everything** from a blank machine to a running app,
with an explanation of *why* each step matters. Follow it top to bottom.

---

## 0. What you need installed first

Install these three things (skip any you already have):

| Tool           | Why                                    | Get it / check                          |
|----------------|----------------------------------------|-----------------------------------------|
| **Python 3.10+** | Runs the FastAPI backend + LangGraph | `python --version`  → download.python.org |
| **Node.js 18+**  | Runs the React frontend              | `node --version`  → nodejs.org          |
| **VS Code**      | The editor you'll work in            | code.visualstudio.com                   |

> On Windows, when installing Python, **tick "Add Python to PATH"** on the first
> installer screen. Without it the `python` command won't work.

**Recommended VS Code extensions** (Extensions panel, `Ctrl/Cmd+Shift+X`):
- *Python* (by Microsoft)
- *ES7+ React/Redux* snippets (optional, nice to have)

---

## 1. Open the project in VS Code

1. Unzip `hcp-crm.zip` somewhere you'll find it (e.g. Desktop).
2. VS Code → **File → Open Folder…** → pick the `hcp-crm` folder.
3. You should see two folders in the sidebar: `backend/` and `frontend/`.

> **Why one folder with two subfolders?** The assignment asks for a single repo
> holding both frontend and backend. Opening the parent folder lets you run two
> terminals side by side — one per service.

---

## 2. Get a free Groq API key (needed for the AI)

1. Go to **https://console.groq.com/keys** and sign in (Google login works).
2. Click **Create API Key**, copy it (starts with `gsk_...`).
3. Keep it handy for Step 4. **Don't paste it into any file you'll push to
   GitHub** — it goes only into `.env`, which is git-ignored.

> **Why Groq?** The assignment mandates it. Groq serves the `gemma2-9b-it` model
> very fast and has a free tier, so the agent's tool-calling stays responsive.

---

## 3. Open a terminal in VS Code

**Terminal → New Terminal** (or `` Ctrl+` ``). A terminal opens at the project
root. You'll open **two** terminals total — one for backend, one for frontend.
Use the **+** icon (or the split icon) in the terminal panel to get a second one.

---

## 4. Set up and run the BACKEND

In your **first terminal**:

```bash
cd backend
```

### 4a. Create a virtual environment
A venv keeps this project's Python packages isolated from the rest of your system.

```bash
python -m venv venv
```

### 4b. Activate it
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **macOS / Linux:** `source venv/bin/activate`

You'll see `(venv)` appear at the start of your terminal line. That means it worked.

> **PowerShell error about scripts being disabled?** Run this once, then retry:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 4c. Install the Python packages

```bash
pip install -r requirements.txt
```

This installs FastAPI, LangGraph, langchain-groq, SQLAlchemy, etc. Takes a minute.

### 4d. Create your `.env` file
Copy the template, then open `.env` in VS Code and paste your key.

- **Windows:** `copy .env.example .env`
- **macOS / Linux:** `cp .env.example .env`

Open `backend/.env` in the editor and set:
```
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=gemma2-9b-it
DATABASE_URL=sqlite:///./hcp_crm.db
```
Leave `DATABASE_URL` as SQLite for now — it works instantly with no DB install.
(Switching to Postgres/MySQL is covered in Section 8.)

### 4e. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

You should see `Uvicorn running on http://127.0.0.1:8000`. Leave this running.

**Verify it:** open **http://localhost:8000/docs** in your browser. You'll see
the interactive API documentation with all endpoints. That's FastAPI confirming
the backend is alive. The SQLite file `hcp_crm.db` is created automatically.

> **Why `--reload`?** It restarts the server whenever you edit a file — handy
> while developing. **Why `/docs`?** FastAPI auto-generates a live API explorer
> from the Pydantic schemas, great for the demo video.

---

## 5. Set up and run the FRONTEND

Open a **second terminal** (the **+** in the terminal panel) so the backend keeps
running in the first one.

```bash
cd frontend
npm install
npm run dev
```

`npm install` downloads React, Redux Toolkit, axios, and Vite (one minute).
`npm run dev` starts the dev server and prints a local URL.

**Open http://localhost:5173** in your browser. You'll see the *Log HCP
Interaction* screen: the structured form on the left, the AI assistant on the right.

> **Why two servers?** The React app (5173) and the API (8000) run separately.
> The frontend calls the backend over HTTP. CORS is already configured in
> `main.py` to allow `localhost:5173`, so they talk to each other cleanly.

---

## 6. Use the app (and what to show in your demo)

**Structured form (left):** fill *HCP name*, pick a sentiment, add topics, click
**Log interaction**. It appears in the *Logged interactions* list below.

**Chat / AI agent (right):** type natural language. Try these — each one triggers
a different one of the **5 LangGraph tools** (watch for the small "tool: …" badge):

| What you type                                                             | Tool that runs      |
|---------------------------------------------------------------------------|---------------------|
| `Met Dr. Smith, discussed Product X efficacy, positive, shared brochure.` | `log_interaction`   |
| `Change interaction 1 sentiment to negative`                              | `edit_interaction`  |
| `Show my interactions`                                                     | `list_interactions` |
| `Suggest follow-ups for interaction 1`                                     | `suggest_follow_ups`|
| `How did the meeting with Dr. Smith go?`                                   | `analyze_sentiment` |

That table is exactly your **"demo of all 5 tools working"** for the video.

---

## 7. Common problems & fixes

| Symptom                                            | Cause / fix                                                            |
|----------------------------------------------------|------------------------------------------------------------------------|
| `python` not found                                 | Reinstall Python with "Add to PATH", or use `python3`.                 |
| `(venv)` doesn't appear                            | Activation command wrong for your shell — see 4b.                     |
| Chat says "Something went wrong reaching the agent" | Backend not running, or `GROQ_API_KEY` missing/invalid in `.env`.     |
| Chat error mentioning the model                    | Model name typo — keep `GROQ_MODEL=gemma2-9b-it`.                     |
| Frontend loads but form does nothing               | Backend not running on port 8000. Start it (Step 4e).                 |
| CORS error in browser console                      | Make sure frontend is on `5173` (Vite default) — it's whitelisted.   |
| `npm` not found                                    | Install Node.js, then restart VS Code.                               |

---

## 8. Optional: switch to PostgreSQL or MySQL

The assignment lists MySQL/Postgres. The code already supports both via
SQLAlchemy — you only change `DATABASE_URL` in `.env`.

**PostgreSQL**
1. Install PostgreSQL, create a database: `createdb hcp_crm`
2. In `.env`:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:YOURPASSWORD@localhost:5432/hcp_crm
   ```
3. Restart the backend. Tables are created automatically on startup.

**MySQL**
1. Install MySQL, then in its shell: `CREATE DATABASE hcp_crm;`
2. In `.env`:
   ```
   DATABASE_URL=mysql+pymysql://root:YOURPASSWORD@localhost:3306/hcp_crm
   ```
3. Restart the backend.

The right driver (`psycopg2-binary` / `pymysql`) is already in `requirements.txt`.

---

## 9. Push to GitHub (for submission)

From the project root (`hcp-crm/`):

```bash
git init
git add .
git commit -m "AI-First CRM HCP module - Log Interaction screen"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

`.gitignore` already excludes `.env`, `node_modules/`, `venv/`, and the `.db`
file, so **your API key and bulky folders won't be uploaded**. Double-check
`.env` is *not* in the commit before pushing.

---

## 10. Recording the video (10–15 min checklist)

1. **Frontend walkthrough** — show the form and the chat panel, log one of each.
2. **All 5 tools** — run the five chat prompts from Section 6; point at each
   tool badge as it appears.
3. **Code explanation** — open `agent.py` (the 5 tools + LangGraph agent),
   `main.py` (endpoints), and `store/interactionSlice.js` (Redux).
4. **What you understood** — one minute summarizing the task in your own words.

That covers every deliverable the assignment asks for.
