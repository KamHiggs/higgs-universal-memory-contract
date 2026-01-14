"""
umc_memory_server.py
Higgs Universal Memory Contract (UMC) reference middleware

What this is:
- A production-ready "memory server" for UMC with PostgreSQL persistence.
- It is NOT an AI assistant. It sits next to your assistant.
- It listens for UMC-style events like STATE_UPDATE, SAVE_NOTE, REQUEST_CONTEXT.
- It stores/retrieves memory per session_id.
- It returns the context your assistant should inject back as <RETRIEVED_CONTEXT> ... </RETRIEVED_CONTEXT>.

Run it locally:
    pip install -r requirements.txt
    export DATABASE_URL="postgresql://umc_user:password@localhost:5432/umc_memory"
    uvicorn middleware.umc_memory_server_v2:app --reload

Then you can hit its endpoints with curl / Postman / your agent code.
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Import database layer
from middleware.database import (
    get_db,
    check_db_health,
    ensure_session_exists,
    get_current_state,
    get_session_notes,
    audit_event,
    UMCNote,
    UMCStateUpdate,
)

app = FastAPI(
    title="UMC Memory Server (Production)",
    description=(
        "Production middleware for the Higgs Universal Memory Contract (UMC). "
        "This is the 'memory infrastructure you control' layer with PostgreSQL persistence."
    ),
    version="1.0.0",
)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class SaveNote(BaseModel):
    """
    UMC SAVE_NOTE
    Assistant is asking us to persist something important.
    """
    type: str  # should be "SAVE_NOTE"
    session_id: str
    scope: str  # "permanent" | "project" | "temporary"
    fact: str
    reason: str
    timestamp: Optional[str] = None  # we can add this server-side if missing


class StateUpdate(BaseModel):
    """
    UMC STATE_UPDATE
    Snapshot of what was decided, what's next, blockers, deadlines.
    """
    type: str  # should be "STATE_UPDATE"
    session_id: str
    summary: str
    next_steps: List[str]
    blockers: List[str]
    deadline: Optional[str] = None
    timestamp: Optional[str] = None


class RequestContext(BaseModel):
    """
    UMC REQUEST_CONTEXT
    Assistant asking us to feed it relevant context.
    """
    type: str  # should be "REQUEST_CONTEXT"
    session_id: str
    topic: str


class RetrievedContextResponse(BaseModel):
    """
    What we send BACK to the assistant.
    The assistant should inject this literally in a block like:
    <RETRIEVED_CONTEXT> ... </RETRIEVED_CONTEXT>
    """
    session_id: str
    context_block: str


# -----------------------------------------------------------------------------
# Helper fns
# -----------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    """
    Basic health / info.
    """
    return {
        "umc": "Higgs Universal Memory Contract middleware (production)",
        "version": "1.0.0",
        "persistence": "PostgreSQL",
        "endpoints": [
            "GET  /health           - database health check",
            "POST /save_note        - store SAVE_NOTE",
            "POST /state_update     - store STATE_UPDATE",
            "POST /request_context  - retrieve context for assistant",
            "GET  /session/{session_id}/memory - inspect memory for debugging",
            "GET  /audit_log        - inspect audit trail (paginated)",
        ],
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """
    Health check endpoint with database status.
    """
    db_health = check_db_health()

    if db_health["status"] != "healthy":
        raise HTTPException(status_code=503, detail="Database unhealthy")

    return {
        "status": "healthy",
        "database": db_health,
        "timestamp": now_iso(),
    }


@app.post("/save_note")
def save_note(note: SaveNote, db: Session = Depends(get_db)):
    """
    Store sticky / project memory for this session_id.
    This is where we enforce privacy, redaction, retention, etc.
    """
    # Ensure session exists
    ensure_session_exists(db, note.session_id)

    # Prepare note data
    timestamp = note.timestamp if note.timestamp else now_iso()

    # Minimal policy example:
    # Don't store obviously sensitive content (keys, passwords, etc.)
    banned_markers = ["password", "secret", "private key", "ssn", "social security"]
    lowered_fact = note.fact.lower()
    rejected = False
    rejected_reason = None

    for marker in banned_markers:
        if marker in lowered_fact:
            rejected = True
            rejected_reason = f"banned marker detected: {marker}"
            break

    # Create note record
    db_note = UMCNote(
        session_id=note.session_id,
        type=note.type,
        scope=note.scope,
        fact=note.fact,
        reason=note.reason,
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        rejected=rejected,
        rejected_reason=rejected_reason,
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Audit
    audit_event(
        db=db,
        event_type="SAVE_NOTE",
        session_id=note.session_id,
        payload={
            "note_id": db_note.id,
            "scope": note.scope,
            "rejected": rejected,
            "timestamp": timestamp,
        }
    )

    return {
        "ok": True,
        "stored": {
            "id": db_note.id,
            "session_id": db_note.session_id,
            "scope": db_note.scope,
            "fact": db_note.fact if not rejected else "[REJECTED]",
            "reason": db_note.reason,
            "rejected": rejected,
            "rejected_reason": rejected_reason,
            "timestamp": timestamp,
        }
    }


@app.post("/state_update")
def state_update(update: StateUpdate, db: Session = Depends(get_db)):
    """
    Store high-level project state (summary, next steps).
    This gives us an auditable timeline of decisions.
    """
    # Ensure session exists
    ensure_session_exists(db, update.session_id)

    # Prepare timestamp
    timestamp = update.timestamp if update.timestamp else now_iso()

    # Create state update record
    db_state = UMCStateUpdate(
        session_id=update.session_id,
        type=update.type,
        summary=update.summary,
        next_steps=update.next_steps,
        blockers=update.blockers,
        deadline=update.deadline,
        timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        is_current=True,  # Trigger will mark old ones as superseded
    )

    db.add(db_state)
    db.commit()
    db.refresh(db_state)

    # Audit
    audit_event(
        db=db,
        event_type="STATE_UPDATE",
        session_id=update.session_id,
        payload={
            "state_update_id": db_state.id,
            "summary": update.summary[:100],  # Truncate for audit
            "next_steps_count": len(update.next_steps),
            "blockers_count": len(update.blockers),
            "timestamp": timestamp,
        }
    )

    return {
        "ok": True,
        "stored": {
            "id": db_state.id,
            "session_id": db_state.session_id,
            "summary": db_state.summary,
            "next_steps": db_state.next_steps,
            "blockers": db_state.blockers,
            "deadline": db_state.deadline,
            "timestamp": timestamp,
        }
    }


@app.post("/request_context", response_model=RetrievedContextResponse)
def request_context(req: RequestContext, db: Session = Depends(get_db)):
    """
    Assistant is saying:
      'I don't want to hallucinate. Give me what we already know.'
    We respond with a combined view of:
    - Latest STATE_UPDATE for this session_id
    - Relevant sticky/project notes for this session_id
    """
    # Ensure session exists
    ensure_session_exists(db, req.session_id)

    # Get latest state update
    latest_state = get_current_state(db, req.session_id)

    # Get all notes for this session
    notes = get_session_notes(db, req.session_id)

    # Build a readable block the assistant can drop into <RETRIEVED_CONTEXT> ... </RETRIEVED_CONTEXT>
    lines = []
    lines.append(f"SESSION_ID: {req.session_id}")
    lines.append(f"TOPIC_REQUESTED: {req.topic}")
    lines.append("")

    if latest_state:
        lines.append("LATEST_STATE_UPDATE:")
        lines.append(f"- summary: {latest_state['summary']}")
        lines.append(f"- next_steps: {', '.join(latest_state['next_steps']) if latest_state['next_steps'] else 'none'}")
        lines.append(f"- blockers: {', '.join(latest_state['blockers']) if latest_state['blockers'] else 'none'}")
        lines.append(f"- deadline: {latest_state['deadline']}")
        lines.append("")
    else:
        lines.append("LATEST_STATE_UPDATE: (none yet)")
        lines.append("")

    if notes:
        lines.append("STICKY_NOTES:")
        for n in notes:
            lines.append(f"- {n['fact']} (scope={n['scope']}, reason={n['reason']})")
        lines.append("")
    else:
        lines.append("STICKY_NOTES: (none yet)")
        lines.append("")

    block = "\n".join(lines)

    # Audit this retrieval request
    audit_event(
        db=db,
        event_type="REQUEST_CONTEXT",
        session_id=req.session_id,
        payload={
            "topic": req.topic,
            "notes_count": len(notes),
            "has_state": latest_state is not None,
            "timestamp": now_iso(),
        }
    )

    return RetrievedContextResponse(
        session_id=req.session_id,
        context_block=f"<RETRIEVED_CONTEXT>\n{block}\n</RETRIEVED_CONTEXT>"
    )


@app.get("/session/{session_id}/memory")
def inspect_session(session_id: str, db: Session = Depends(get_db)):
    """
    Debug / introspection endpoint.
    Lets you see what has been stored for a given session_id.
    DO NOT expose this publicly without auth in production.
    """
    # Get current state
    state = get_current_state(db, session_id)

    # Get notes
    notes = get_session_notes(db, session_id)

    return {
        "session_id": session_id,
        "current_state": state,
        "notes": notes,
        "notes_count": len(notes),
    }


@app.get("/audit_log")
def inspect_audit_log(
    limit: int = 100,
    offset: int = 0,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Debug: show audit trail (paginated).
    In production this should be protected or exported to an audit system.
    """
    from middleware.database import UMCAuditLog

    query = db.query(UMCAuditLog)

    if session_id:
        query = query.filter(UMCAuditLog.session_id == session_id)

    total_count = query.count()

    events = (
        query
        .order_by(UMCAuditLog.timestamp.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "session_id": e.session_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "payload": e.payload,
            }
            for e in events
        ],
    }


# -----------------------------------------------------------------------------
# Startup / Shutdown
# -----------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    Run on server startup.
    """
    print("🚀 UMC Memory Server starting...")
    print(f"   Version: 1.0.0")
    print(f"   Persistence: PostgreSQL")

    # Check database health
    health = check_db_health()
    if health["status"] == "healthy":
        print(f"   ✅ Database: {health['database_url']}")
        print(f"   ✅ Latency: {health['latency_ms']}ms")
    else:
        print(f"   ❌ Database: {health.get('error', 'unknown error')}")
        print(f"   ⚠️  Server will start but /health will fail")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on server shutdown.
    """
    print("👋 UMC Memory Server shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
