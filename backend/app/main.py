from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.db.database import connect_db, close_db


# ---------------------------------------------------------------------------
# Rate limiter keyed by X-Session-ID header (falls back to IP)
# ---------------------------------------------------------------------------
def _session_key(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        return session_id
    return get_remote_address(request)


limiter = Limiter(key_func=_session_key, default_limits=["10/minute"])


# ---------------------------------------------------------------------------
# Lifespan: DB connect / disconnect
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await connect_db()
    yield
    await close_db()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="CircuiTech API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Session-ID validation dependency
# ---------------------------------------------------------------------------
def _validate_session_id(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-ID header.")
    try:
        UUID(session_id, version=4)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid X-Session-ID; must be a UUID v4."
        )
    return session_id


# ---------------------------------------------------------------------------
# Chat router
# ---------------------------------------------------------------------------
from app.agents.bom_agent import run_bom_agent
from app.models.chat import ChatRequest, ChatResponse
from app.db.database import update_design_session

chat_router = APIRouter(prefix="/api/chat", tags=["chat"])


@chat_router.post("/")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    chat_req: ChatRequest,
    session_id: str = Depends(_validate_session_id),
):
    try:
        # Run the BOM agent to see if it can generate a BOM from the user's message, passing history
        agent_result = await run_bom_agent(user_prompt=chat_req.message, history=chat_req.history)
        
        # Build the new conversation history
        new_history = chat_req.history + [
            {"role": "user", "content": chat_req.message},
            {"role": "assistant", "content": agent_result.reply}
        ]
        
        # Persist session to MongoDB
        await update_design_session(
            session_id=session_id,
            chat_history=new_history,
            bom=[item.model_dump(by_alias=True) for item in agent_result.items] if agent_result.items else []
        )
        
        return ChatResponse(
            session_id=session_id,
            reply=agent_result.reply,
            bom=agent_result,
            status="success"
        ).model_dump(by_alias=True)
        
    except Exception as e:
        # If the LLM didn't understand as a BOM request or failed parsing, just return a generic chat reply
        return ChatResponse(
            session_id=session_id,
            reply=f"I encountered an issue parsing that request. Could you clarify what you need? (Error: {str(e)})",
            bom=None,
            status="error"
        ).model_dump(by_alias=True)

app.include_router(chat_router)

# ---------------------------------------------------------------------------
# Pinmap router
# ---------------------------------------------------------------------------
from app.agents.pinmap_agent import run_pinmap_agent
from app.models.pinmap import PinMap
from typing import List, Dict, Any
from pydantic import BaseModel, Field

pinmap_router = APIRouter(prefix="/api/pinmap", tags=["pinmap"])

class PinMapRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(..., description="Array of BOM items")

@pinmap_router.post("/")
@limiter.limit("5/minute")
async def generate_pinmap(
    request: Request,
    pinmap_req: PinMapRequest,
    session_id: str = Depends(_validate_session_id),
):
    try:
        # Send the BOM list to the pinmap agent
        result = await run_pinmap_agent(bom_items=pinmap_req.items)
        return result.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(pinmap_router)
