"""
models.py
---------
The database table(s). We keep one main table, `interactions`, which stores
every logged HCP (Healthcare Professional) interaction.

List-type fields (attendees, topics, materials, samples, follow-ups) are stored
as JSON so a single row holds the whole interaction. This keeps the schema
simple and works identically on SQLite, Postgres, and MySQL.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    hcp_name = Column(String(255), nullable=False)
    interaction_type = Column(String(100), default="Meeting")   # Meeting, Call, Email, etc.
    date = Column(String(50), nullable=True)                     # e.g. "2025-04-19"
    time = Column(String(50), nullable=True)                     # e.g. "19:36"

    attendees = Column(JSON, default=list)                       # ["Dr. Smith", "Rep A"]
    topics_discussed = Column(Text, default="")                  # free text / key points
    materials_shared = Column(JSON, default=list)                # ["Product X brochure"]
    samples_distributed = Column(JSON, default=list)             # ["Sample A x5"]

    sentiment = Column(String(50), default="Neutral")            # Positive / Neutral / Negative
    outcomes = Column(Text, default="")                          # key outcomes / agreements
    follow_up_actions = Column(JSON, default=list)               # ["Send Phase III PDF"]

    ai_summary = Column(Text, default="")                        # LLM-generated summary

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert the row into a plain dict for JSON responses."""
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "interaction_type": self.interaction_type,
            "date": self.date,
            "time": self.time,
            "attendees": self.attendees or [],
            "topics_discussed": self.topics_discussed or "",
            "materials_shared": self.materials_shared or [],
            "samples_distributed": self.samples_distributed or [],
            "sentiment": self.sentiment,
            "outcomes": self.outcomes or "",
            "follow_up_actions": self.follow_up_actions or [],
            "ai_summary": self.ai_summary or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
