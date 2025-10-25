"""
umc_memory_server.py
Higgs Universal Memory Contract (UMC) reference middleware

What this is:
- A minimal in-memory "memory server" for UMC.
- It is NOT an AI assistant. It sits next to your assistant.
- It listens for UMC-style events like STATE_UPDATE, SAVE_NOTE, REQUEST_CONTEXT.
- It stores/retrieves memory per session_id.
- It returns the context your assistant should inject back as <RETRIEVED_CONTEXT> ... </RETRIEVED_CONTEXT>.

This file is intentionally simple so people can read it, fork it, and build on it.
In production you’d likely:
- persist to SQLite / Postgres / vector DB instead of Python dict
- add auth
- add retention policy enforcement
- add audit export

Run it locally:
    pip install fastapi uvicorn
    uvicorn umc_memory_server:app --reload

Then you can hit its endpoints with curl / Postman / your agent code.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI(
    title="UMC Memory Server (Reference)",
    description=(
        "Reference middleware for the Higgs Universal Memory Contract (UMC). "
        "This is the 'memory infrastructure you control' layer."
    ),
    version="0.9-core",
)

# -----------------------------------------------------------------------------
# Internal storage
# -----------------------------------------------------------------------------
# In-memory stores (replace with DB in production)
SESSION_NOTES: Dict[str, List[Dict]] = {}          # sticky memory / SAVE_NOTE
SESSION_STATE_UPDATES: Dict[str, List[Dict]] = {}  # timeline of STATE_UPDATE blocks
AUDIT_LOG: List[Dict] = []                         # append-only audit events


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
    <RETRIEVED_CONTEXT>
    ...
    </RETRIEVED_CONTEXT>
    """
    session_id: str
    context_block: str


# -----------------------------------------------------------------------------
# Helper fns
# -----------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def audit(event_type: str, payload: dict):
    AUDIT_LOG.append(
        {
            "event_type": event_type,
            "timestamp": now_iso(),
            "payload": payload,
        }
    )


def ensure_session(session_id: str):
    if session_id not in SESSION_NOTES:
        SESSION_NOTES[session_id] = []
    if session_id not in SESSION_STATE_UPDATES:
        SESSION_STATE_UPDATES[session_id] = []


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    """
    Basic health / info.
    """
    return {
        "umc": "Higgs Universal Memory Contract middleware reference",
        "version": "0.9-core",
        "endpoints": [
            "POST /save_note        - store SAVE_NOTE",
            "POST /state_update     - store STATE_UPDATE",
            "POST /request_context  - retrieve context for assistant",
            "GET  /session/{session_id}/memory - inspect memory for debugging",
            "GET  /audit_log        - inspect audit trail (not for prod)",
        ],
    }


@app.post("/save_note")
def save_note(note: SaveNote):
    """
    Store sticky / project memory for this session_id.
    This is where we'd enforce privacy, redaction, retention, etc.
    """
    ensure_session(note.session_id)

    entry = note.dict()
    if not entry.get("timestamp"):
        entry["timestamp"] = now_iso()

    # Minimal policy example:
    # Don't store obviously sensitive content (keys, passwords, etc.)
    banned_markers = ["password", "secret", "private key", "ssn", "social security"]
    lowered_fact = entry["fact"].lower()
    for marker in banned_markers:
        if marker in lowered_fact:
            entry["rejected"] = True
            entry["rejected_reason"] = f"banned marker detected: {marker}"
            break

    SESSION_NOTES[note.session_id].append(entry)
    audit("SAVE_NOTE", entry)
    return {"ok": True, "stored": entry}


@app.post("/state_update")
def state_update(update: StateUpdate):
    """
    Store high-level project state (summary, next steps).
    This gives us an auditable timeline of decisions.
    """
    ensure_session(update.session_id)

    entry = update.dict()
    if not entry.get("timestamp"):
        entry["timestamp"] = now_iso()

    SESSION_STATE_UPDATES[update.session_id].append(entry)
    audit("STATE_UPDATE", entry)
    return {"ok": True, "stored": entry}


@app.post("/request_context", response_model=RetrievedContextResponse)
def request_context(req: RequestContext):
    """
    Assistant is saying:
      'I don't want to hallucinate. Give me what we already know.'
    We respond with a combined view of:
    - Latest STATE_UPDATE for this session_id
    - Relevant sticky/project notes for this session_id
    """
    ensure_session(req.session_id)

    # get latest state update if any
    state_updates = SESSION_STATE_UPDATES[req.session_id]
    latest_state = state_updates[-1] if state_updates else None

    # gather all notes for this session
    notes = SESSION_NOTES[req.session_id]

    # build a readable block the assistant can drop into <RETRIEVED_CONTEXT>...</RETRIEVED_CONTEXT>
    lines = []
    lines.append(f"SESSION_ID: {req.session_id}")
    lines.append(f"TOPIC_REQUESTED: {req.topic}")
    lines.append("")

    if latest_state:
        lines.append("LATEST_STATE_UPDATE:")
        lines.append(f"- summary: {latest_state['summary']}")
        lines.append(f"- next_steps: {', '.join(latest_state['next_steps'])}")
        lines.append(f"- blockers: {', '.join(latest_state['blockers']) if latest_state['blockers'] else 'none'}")
        lines.append(f"- deadline: {latest_state['deadline']}")
        lines.append("")
    else:
        lines.append("LATEST_STATE_UPDATE: (none yet)")
        lines.append("")

    if notes:
        lines.append("STICKY_NOTES:")
        for n in notes:
            # Only include notes that weren't rejected
            if n.get("rejected"):
                continue
            lines.append(f"- {n['fact']} (scope={n['scope']}, reason={n['reason']})")
        lines.append("")
    else:
        lines.append("STICKY_NOTES: (none yet)")
        lines.append("")

    block = "\n".join(lines)

    # Audit this retrieval request
    audit(
        "REQUEST_CONTEXT",
        {
            "session_id": req.session_id,
            "topic": req.topic,
            "timestamp": now_iso(),
        },
    )

    return RetrievedContextResponse(
        session_id=req.session_id,
        context_block=f"<RETRIEVED_CONTEXT>\n{block}\n</RETRIEVED_CONTEXT>"
    )


@app.get("/session/{session_id}/memory")
def inspect_session(session_id: str):
    """
    Debug / introspection endpoint.
    Lets you see what has been stored for a given session_id.
    DO NOT expose this publicly without auth in production.
    """
    ensure_session(session_id)
    return {
        "session_id": session_id,
        "state_updates": SESSION_STATE_UPDATES[session_id],
        "notes": SESSION_NOTES[session_id],
    }


@app.get("/audit_log")
def inspect_audit_log():
    """
    Debug: show full audit trail.
    In production this should be protected or exported to an audit system.
    """
    return {
        "count": len(AUDIT_LOG),
        "events": AUDIT_LOG,
    }
