"""
main.py
-------
The FastAPI application. It exposes two ways to log an HCP interaction, exactly
as the assignment asks:

  1. STRUCTURED FORM  -> plain REST endpoints (/interactions ...)
  2. CONVERSATIONAL   -> /chat, which runs the LangGraph agent

Run it with:
    uvicorn main:app --reload --port 8000
Then open http://localhost:8000/docs for the interactive API docs.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Interaction
import schemas
from agent import run_agent

# Create tables on startup (no migrations needed for this assignment).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM — HCP Module", version="1.0.0")

# Allow the React dev server (Vite runs on 5173) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "message": "HCP CRM backend running"}


# ---------------------------------------------------------------------------
# STRUCTURED FORM endpoints (Redux calls these)
# ---------------------------------------------------------------------------
@app.post("/interactions")
def create_interaction(payload: schemas.InteractionCreate, db: Session = Depends(get_db)):
    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction.to_dict()


@app.get("/interactions")
def get_interactions(db: Session = Depends(get_db)):
    rows = db.query(Interaction).order_by(Interaction.id.desc()).all()
    return [r.to_dict() for r in rows]


@app.get("/interactions/{interaction_id}")
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    row = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return row.to_dict()


@app.put("/interactions/{interaction_id}")
def update_interaction(
    interaction_id: int,
    payload: schemas.InteractionUpdate,
    db: Session = Depends(get_db),
):
    row = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Only update the fields the client actually sent.
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row.to_dict()


@app.delete("/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    row = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(row)
    db.commit()
    return {"deleted": interaction_id}


# ---------------------------------------------------------------------------
# CONVERSATIONAL endpoint (LangGraph agent)
# ---------------------------------------------------------------------------
@app.post("/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest):
    """Send a natural-language message to the LangGraph agent."""
    try:
        result = run_agent(payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")
    return schemas.ChatResponse(
        reply=result["reply"],
        interaction=result["interaction"],
        tool_used=result["tool_used"],
        deleted_id=result["deleted_id"],
    )
