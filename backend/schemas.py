"""
schemas.py
----------
Pydantic models. These define the *shape* of the data going in and out of the
API. FastAPI uses them to validate requests automatically and to generate the
interactive docs at /docs.
"""

from typing import List, Optional
from pydantic import BaseModel


class InteractionBase(BaseModel):
    hcp_name: str
    interaction_type: Optional[str] = "Meeting"
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[List[str]] = []
    topics_discussed: Optional[str] = ""
    materials_shared: Optional[List[str]] = []
    samples_distributed: Optional[List[str]] = []
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = ""
    follow_up_actions: Optional[List[str]] = []


class InteractionCreate(InteractionBase):
    """Used when creating a new interaction from the structured form."""
    pass


class InteractionUpdate(BaseModel):
    """All fields optional so you can patch just one thing."""
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[List[str]] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[str]] = None
    samples_distributed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[List[str]] = None


class ChatRequest(BaseModel):
    """A message sent to the conversational AI agent."""
    message: str


class ChatResponse(BaseModel):
    reply: str
    interaction: Optional[dict] = None      # the interaction the agent created/edited, if any
    tool_used: Optional[str] = None         # which LangGraph tool ran (for the demo)
