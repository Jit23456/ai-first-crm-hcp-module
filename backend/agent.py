"""
agent.py
--------
The LangGraph AI agent and its tools. THIS FILE IS THE HEART OF THE ASSIGNMENT.

WHAT THE AGENT DOES (its role):
    The agent is the "brain" behind the chat interface on the Log Interaction
    screen. A field rep can type plain English like:
        "Met Dr. Smith today, discussed Product X efficacy, positive sentiment,
         shared the brochure. Follow up in 2 weeks."
    The agent reads that, decides which tool(s) to call, extracts the structured
    fields with the LLM, writes them to the database, and replies in natural
    language. It manages the full lifecycle of an HCP interaction: create, read,
    edit, enrich, and recommend next steps.

HOW IT WORKS (LangGraph):
    We use LangGraph's prebuilt ReAct agent (create_react_agent). It runs a loop:
        1. LLM reads the conversation + the list of available tools
        2. LLM decides: answer directly, OR call a tool with arguments
        3. If a tool is called, LangGraph runs it and feeds the result back
        4. Loop continues until the LLM produces a final answer
    LangGraph handles the state (message history) and the routing between the
    "reason" step and the "act" (tool) step.

THE 5 TOOLS (assignment requires min. 5, two of which are mandatory):
    1. log_interaction     (MANDATORY) - create a new interaction; LLM extracts
                                          entities + writes an AI summary
    2. edit_interaction    (MANDATORY) - modify an already-logged interaction
    3. list_interactions               - search / retrieve past interactions
    4. suggest_follow_ups              - LLM proposes next-step actions
    5. analyze_sentiment               - LLM classifies HCP sentiment from notes
"""

import os
import json
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from database import SessionLocal
from models import Interaction

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# The LLM. gemma2-9b-it (the model the assignment mandated) was decommissioned
# by Groq, so llama-3.3-70b-versatile is the default now. Override in .env.
llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0.2,
)

# We track which tool ran last, purely so the /chat endpoint can report it in
# the demo ("tool_used"). In a bigger app you'd pull this from the run trace.
_LAST_TOOL_USED = {"name": None, "interaction": None}


def _reset_tool_tracker():
    _LAST_TOOL_USED["name"] = None
    _LAST_TOOL_USED["interaction"] = None


# ---------------------------------------------------------------------------
# LLM helper: extract structured fields from a free-text note
# ---------------------------------------------------------------------------
def _extract_fields_with_llm(text: str) -> dict:
    """
    Ask the LLM to turn a messy sentence into clean structured fields.
    This is the 'entity extraction' part of the Log Interaction tool.
    """
    prompt = f"""You are a data-extraction assistant for a pharma CRM.
Extract the following fields from the rep's note and reply with ONLY valid JSON
(no markdown, no commentary). Use empty string or empty list when a field is absent.

Fields:
- hcp_name (string)
- interaction_type (one of: Meeting, Call, Email, Conference, Other)
- attendees (list of strings)
- topics_discussed (string)
- materials_shared (list of strings)
- samples_distributed (list of strings)
- sentiment (one of: Positive, Neutral, Negative)
- outcomes (string)
- follow_up_actions (list of strings)

Rep's note:
\"\"\"{text}\"\"\"
"""
    resp = llm.invoke(prompt)
    raw = resp.content.strip()

    # Models sometimes wrap JSON in ```json fences — strip them defensively.
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw[raw.find("{"): raw.rfind("}") + 1]

    try:
        return json.loads(raw)
    except Exception:
        # Fallback: never crash the tool, just store the raw note.
        return {"hcp_name": "Unknown HCP", "topics_discussed": text}


# ---------------------------------------------------------------------------
# TOOL 1 (MANDATORY): Log Interaction
# ---------------------------------------------------------------------------
@tool
def log_interaction(note: str) -> str:
    """Log a NEW HCP interaction from a natural-language note.
    Use this when the rep describes a meeting/call that just happened.
    It extracts structured fields with the LLM, writes an AI summary, and
    saves everything to the database. Returns a confirmation with the new ID."""
    fields = _extract_fields_with_llm(note)

    # A short AI summary of the interaction (LLM summarization).
    summary_resp = llm.invoke(
        f"Summarize this HCP interaction in one crisp sentence for a CRM log:\n{note}"
    )
    ai_summary = summary_resp.content.strip()

    db = SessionLocal()
    try:
        interaction = Interaction(
            hcp_name=fields.get("hcp_name") or "Unknown HCP",
            interaction_type=fields.get("interaction_type") or "Meeting",
            attendees=fields.get("attendees") or [],
            topics_discussed=fields.get("topics_discussed") or "",
            materials_shared=fields.get("materials_shared") or [],
            samples_distributed=fields.get("samples_distributed") or [],
            sentiment=fields.get("sentiment") or "Neutral",
            outcomes=fields.get("outcomes") or "",
            follow_up_actions=fields.get("follow_up_actions") or [],
            ai_summary=ai_summary,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        result = interaction.to_dict()
    finally:
        db.close()

    _LAST_TOOL_USED["name"] = "log_interaction"
    _LAST_TOOL_USED["interaction"] = result
    return (
        f"Logged interaction #{result['id']} with {result['hcp_name']}. "
        f"Sentiment: {result['sentiment']}. Summary: {result['ai_summary']}"
    )


# ---------------------------------------------------------------------------
# TOOL 2 (MANDATORY): Edit Interaction
# ---------------------------------------------------------------------------
@tool
def edit_interaction(interaction_id: int, instruction: str) -> str:
    """Edit an EXISTING interaction by its ID.
    Use this when the rep wants to change/correct a logged interaction, e.g.
    'change interaction 3 sentiment to negative' or 'add a follow-up to #5'.
    The LLM interprets the change instruction against the current record."""
    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"No interaction found with ID {interaction_id}."

        current = interaction.to_dict()
        prompt = f"""You are editing a CRM record. Here is the current record as JSON:
{json.dumps(current)}

Apply this change instruction: "{instruction}"

Reply with ONLY the full updated record as valid JSON (same keys). Keep unchanged
fields exactly as they are."""
        resp = llm.invoke(prompt)
        raw = resp.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw[raw.find("{"): raw.rfind("}") + 1]
        updated = json.loads(raw)

        # Apply the editable fields back onto the row.
        for key in [
            "hcp_name", "interaction_type", "date", "time", "attendees",
            "topics_discussed", "materials_shared", "samples_distributed",
            "sentiment", "outcomes", "follow_up_actions",
        ]:
            if key in updated:
                setattr(interaction, key, updated[key])

        db.commit()
        db.refresh(interaction)
        result = interaction.to_dict()
    finally:
        db.close()

    _LAST_TOOL_USED["name"] = "edit_interaction"
    _LAST_TOOL_USED["interaction"] = result
    return f"Updated interaction #{result['id']}. New state: {json.dumps(result)}"


# ---------------------------------------------------------------------------
# TOOL 3: List / Search Interactions
# ---------------------------------------------------------------------------
@tool
def list_interactions(hcp_name: str = "") -> str:
    """Retrieve logged interactions. Optionally filter by HCP name (partial match).
    Use this when the rep asks 'show my interactions' or 'what did I log for Dr. Smith?'."""
    db = SessionLocal()
    try:
        query = db.query(Interaction)
        if hcp_name:
            query = query.filter(Interaction.hcp_name.ilike(f"%{hcp_name}%"))
        rows = query.order_by(Interaction.id.desc()).limit(10).all()
        results = [r.to_dict() for r in rows]
    finally:
        db.close()

    _LAST_TOOL_USED["name"] = "list_interactions"
    if not results:
        return "No interactions found."
    lines = [
        f"#{r['id']} | {r['hcp_name']} | {r['interaction_type']} | "
        f"{r['sentiment']} | {r['ai_summary']}"
        for r in results
    ]
    return "Found interactions:\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# TOOL 4: Suggest Follow-ups
# ---------------------------------------------------------------------------
@tool
def suggest_follow_ups(interaction_id: int) -> str:
    """Generate AI-suggested follow-up actions for a specific interaction ID.
    Use when the rep asks 'what should I do next for interaction 4?'."""
    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"No interaction found with ID {interaction_id}."
        data = interaction.to_dict()
    finally:
        db.close()

    resp = llm.invoke(
        f"""Based on this HCP interaction, suggest 3 concrete, sales-relevant
follow-up actions for a pharma field rep. Be specific and brief (one line each).
Interaction: {json.dumps(data)}"""
    )
    _LAST_TOOL_USED["name"] = "suggest_follow_ups"
    return f"Suggested follow-ups for #{interaction_id}:\n{resp.content.strip()}"


# ---------------------------------------------------------------------------
# TOOL 5: Analyze Sentiment
# ---------------------------------------------------------------------------
@tool
def analyze_sentiment(text: str) -> str:
    """Classify the HCP's sentiment (Positive / Neutral / Negative) from a note
    and give a one-line reason. Use when the rep asks to gauge how a meeting went."""
    resp = llm.invoke(
        f"""Classify the HCP sentiment in this note as Positive, Neutral, or Negative,
then give a one-line reason. Format: 'SENTIMENT — reason'.
Note: {text}"""
    )
    _LAST_TOOL_USED["name"] = "analyze_sentiment"
    return resp.content.strip()


# ---------------------------------------------------------------------------
# Build the LangGraph agent
# ---------------------------------------------------------------------------
TOOLS = [
    log_interaction,
    edit_interaction,
    list_interactions,
    suggest_follow_ups,
    analyze_sentiment,
]

SYSTEM_PROMPT = """You are the AI assistant inside an AI-first pharma CRM, helping
a field sales representative log and manage interactions with Healthcare
Professionals (HCPs). You are precise, compliant, and concise.

Rules:
- When the rep describes a NEW meeting/call, use log_interaction.
- When they want to change something already logged, use edit_interaction (you
  need the interaction ID; if you don't have it, ask or use list_interactions).
- Use list_interactions to look things up.
- Use suggest_follow_ups when asked what to do next.
- Use analyze_sentiment to gauge how an interaction went.
- Always confirm what you did in plain, friendly language."""

# create_react_agent wires the LLM + tools into a runnable LangGraph graph.
agent_graph = create_react_agent(llm, TOOLS, state_modifier=SYSTEM_PROMPT)


def run_agent(message: str) -> dict:
    """Entry point used by the FastAPI /chat endpoint.
    Runs the agent on a single user message and returns the reply plus which
    tool ran and any interaction that was created/edited (for the UI + demo)."""
    _reset_tool_tracker()
    result = agent_graph.invoke({"messages": [("user", message)]})
    final_message = result["messages"][-1].content
    return {
        "reply": final_message,
        "tool_used": _LAST_TOOL_USED["name"],
        "interaction": _LAST_TOOL_USED["interaction"],
    }
