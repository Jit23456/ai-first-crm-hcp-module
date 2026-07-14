# AI-First CRM — HCP Module (Log Interaction Screen)

An AI-first Customer Relationship Management screen for pharma field
representatives to log interactions with **Healthcare Professionals (HCPs)**.
Interactions can be logged **two ways**:

1. **Structured form** — the classic fields (HCP name, sentiment, topics, etc.)
2. **Conversational chat** — type a plain-English note and a **LangGraph AI
   agent** extracts the fields, summarizes, and saves it.

## Tech stack

| Layer      | Technology                                              |
|------------|---------------------------------------------------------|
| Frontend   | React + Redux Toolkit (Vite), Google **Inter** font     |
| Backend    | Python + **FastAPI**                                    |
| AI agent   | **LangGraph** (ReAct agent)                             |
| LLM        | **Groq** — `llama-3.3-70b-versatile` (default)          |
| Database   | SQLAlchemy → **SQLite / PostgreSQL / MySQL**            |

---

## The LangGraph agent

The agent is the brain behind the chat panel. It reads the rep's message,
decides which tool to call, runs it, and replies in natural language. It manages
the full lifecycle of an HCP interaction: create, read, edit, delete, enrich,
recommend.

### The 6 tools (`backend/agent.py`)

1. **`log_interaction`** *(mandatory)* — creates a new interaction from a
   free-text note. Uses the LLM for **entity extraction** (HCP name, sentiment,
   topics, materials, follow-ups) and **summarization** (one-line AI summary).
2. **`edit_interaction`** *(mandatory)* — modifies a logged interaction by ID.
   The LLM interprets the change instruction against the current record.
3. **`list_interactions`** — retrieves / searches past interactions.
4. **`suggest_follow_ups`** — LLM proposes concrete next-step actions.
5. **`analyze_sentiment`** — LLM classifies HCP sentiment with a reason.
6. **`delete_interaction`** — removes a logged interaction by ID (the agent
   looks up the ID via `list_interactions` if you only give a name).

---

## Project structure

```
hcp-crm/
├── backend/
│   ├── main.py            FastAPI app + REST + /chat endpoints
│   ├── agent.py           LangGraph agent + the 6 tools  ← core
│   ├── models.py          SQLAlchemy Interaction table
│   ├── schemas.py         Pydantic request/response models
│   ├── database.py        DB engine/session (SQLite/Postgres/MySQL)
│   ├── requirements.txt
│   └── .env.example       copy to .env and fill in
└── frontend/
    ├── index.html         loads Inter font
    ├── package.json
    └── src/
        ├── App.jsx
        ├── api/api.js
        ├── store/         Redux store + slice (thunks)
        └── components/    Form, Chat, List
```

---

## How to run

> Prerequisites: **Python 3.10+**, **Node.js 18+**, and a free Groq API key
> from https://console.groq.com/keys.
> See `SETUP_GUIDE.md` for the full step-by-step walkthrough.

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your Groq API key into .env
uvicorn main:app --reload --port 8000
```

Backend runs at http://localhost:8000 (interactive API docs at `/docs`).

### 2. Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

---

## Environment variables (`backend/.env`)

```
GROQ_API_KEY=your_key_from_console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./hcp_crm.db
```

The database defaults to **SQLite** so it runs with zero setup. To use
PostgreSQL or MySQL, just change `DATABASE_URL` (examples in `.env.example`).
Never commit your real `.env` — it is gitignored; only `.env.example` (with a
placeholder key) belongs in the repo.

---

## Try it

**Structured:** fill the left form and click *Log interaction*.

**Chat (agent):** type into the right panel, e.g.
- `Met Dr. Smith today, discussed Product X efficacy, positive sentiment, shared the brochure. Follow up in 2 weeks.`
- `Show my interactions`
- `Change interaction 1 sentiment to negative`
- `Suggest follow-ups for interaction 1`
- `How did the meeting with Dr. Smith go?`
- `Delete interaction 2`

Each reply shows a **tool badge** so you can see which of the 6 tools ran.
