from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.models.bom import AgentResponse

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's input message to the Co-Pilot.")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Array of past messages.")

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    bom: Optional[AgentResponse] = None
    status: str = Field(default="success", description="Indicates processing status")
