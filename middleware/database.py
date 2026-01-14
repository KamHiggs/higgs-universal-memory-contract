"""
database.py
SQLAlchemy models and database connection for UMC Memory Server

Provides:
- Database connection/session management
- ORM models for UMC tables (sessions, notes, state_updates, audit_log)
- Connection health checks
"""

import os
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    Text,
    Boolean,
    Integer,
    TIMESTAMP,
    JSON,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://umc_user:umc_password_change_me@localhost:5432/umc_memory"
)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# Models
# =============================================================================

class UMCSession(Base):
    """UMC session registry"""
    __tablename__ = "umc_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(Text, unique=True, nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user_id = Column(Text)
    assistant_id = Column(Text)
    project_id = Column(Text)

    status = Column(Text, default="active", nullable=False)
    retention_policy = Column(Text, default="standard")
    expires_at = Column(TIMESTAMP(timezone=True))

    note_count = Column(Integer, default=0)
    state_update_count = Column(Integer, default=0)
    last_note_at = Column(TIMESTAMP(timezone=True))
    last_state_update_at = Column(TIMESTAMP(timezone=True))


class UMCNote(Base):
    """UMC SAVE_NOTE events"""
    __tablename__ = "umc_notes"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(Text, nullable=False, index=True)

    type = Column(Text, default="SAVE_NOTE", nullable=False)
    scope = Column(Text, nullable=False)  # 'permanent', 'project', 'temporary'
    fact = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    rejected = Column(Boolean, default=False)
    rejected_reason = Column(Text)
    contains_pii = Column(Boolean, default=False)
    redacted = Column(Boolean, default=False)

    deleted_at = Column(TIMESTAMP(timezone=True))


Index('idx_umc_notes_session_id', UMCNote.session_id)
Index('idx_umc_notes_scope', UMCNote.scope)
Index('idx_umc_notes_timestamp', UMCNote.timestamp.desc())


class UMCStateUpdate(Base):
    """UMC STATE_UPDATE events"""
    __tablename__ = "umc_state_updates"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(Text, nullable=False, index=True)

    type = Column(Text, default="STATE_UPDATE", nullable=False)
    summary = Column(Text, nullable=False)
    next_steps = Column(JSON, default=list, nullable=False)  # Array of strings
    blockers = Column(JSON, default=list, nullable=False)    # Array of strings
    deadline = Column(Text)

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    superseded_by_id = Column(BigInteger)
    is_current = Column(Boolean, default=True)


Index('idx_umc_state_updates_session_id', UMCStateUpdate.session_id)
Index('idx_umc_state_updates_timestamp', UMCStateUpdate.timestamp.desc())


class UMCAuditLog(Base):
    """UMC audit trail"""
    __tablename__ = "umc_audit_log"

    id = Column(BigInteger, primary_key=True, index=True)

    event_type = Column(Text, nullable=False)
    session_id = Column(Text)

    payload = Column(JSON, nullable=False)

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user_agent = Column(Text)
    ip_address = Column(Text)  # Using Text instead of INET for simplicity
    request_id = Column(Text)


Index('idx_umc_audit_log_session_id', UMCAuditLog.session_id)
Index('idx_umc_audit_log_event_type', UMCAuditLog.event_type)
Index('idx_umc_audit_log_timestamp', UMCAuditLog.timestamp.desc())


# =============================================================================
# Database Connection Management
# =============================================================================

def get_db() -> Session:
    """
    FastAPI dependency for database sessions.

    Usage in FastAPI:
        @app.post("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create tables).
    Only use in development. In production, use migrations.
    """
    Base.metadata.create_all(bind=engine)


def check_db_health() -> dict:
    """
    Check database connection health.

    Returns:
        dict with status, latency, table counts
    """
    try:
        db = SessionLocal()
        start = datetime.now()

        # Simple query to test connection
        db.execute("SELECT 1")

        # Get table counts
        session_count = db.query(UMCSession).count()
        note_count = db.query(UMCNote).count()
        state_update_count = db.query(UMCStateUpdate).count()
        audit_count = db.query(UMCAuditLog).count()

        latency_ms = (datetime.now() - start).total_seconds() * 1000

        db.close()

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "database_url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "unknown",
            "tables": {
                "sessions": session_count,
                "notes": note_count,
                "state_updates": state_update_count,
                "audit_log": audit_count,
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "unknown",
        }


def ensure_session_exists(db: Session, session_id: str) -> UMCSession:
    """
    Ensure a session exists in the database, create if not.

    Args:
        db: Database session
        session_id: Session identifier

    Returns:
        UMCSession object
    """
    session = db.query(UMCSession).filter(UMCSession.session_id == session_id).first()

    if not session:
        session = UMCSession(
            session_id=session_id,
            status="active",
            created_at=func.now(),
            last_activity_at=func.now()
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return session


# =============================================================================
# Utility Functions
# =============================================================================

def get_current_state(db: Session, session_id: str) -> Optional[dict]:
    """
    Get current state update for a session.

    Args:
        db: Database session
        session_id: Session identifier

    Returns:
        dict with current state or None
    """
    state = (
        db.query(UMCStateUpdate)
        .filter(UMCStateUpdate.session_id == session_id)
        .filter(UMCStateUpdate.is_current == True)
        .order_by(UMCStateUpdate.timestamp.desc())
        .first()
    )

    if not state:
        return None

    return {
        "summary": state.summary,
        "next_steps": state.next_steps,
        "blockers": state.blockers,
        "deadline": state.deadline,
        "timestamp": state.timestamp.isoformat() if state.timestamp else None,
    }


def get_session_notes(db: Session, session_id: str) -> list[dict]:
    """
    Get all active notes for a session.

    Args:
        db: Database session
        session_id: Session identifier

    Returns:
        List of note dicts
    """
    notes = (
        db.query(UMCNote)
        .filter(UMCNote.session_id == session_id)
        .filter(UMCNote.rejected == False)
        .filter(UMCNote.deleted_at == None)
        .order_by(UMCNote.timestamp.desc())
        .all()
    )

    return [
        {
            "fact": note.fact,
            "scope": note.scope,
            "reason": note.reason,
            "timestamp": note.timestamp.isoformat() if note.timestamp else None,
        }
        for note in notes
    ]


def audit_event(
    db: Session,
    event_type: str,
    payload: dict,
    session_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
):
    """
    Log an audit event.

    Args:
        db: Database session
        event_type: Type of event (e.g., 'SAVE_NOTE', 'STATE_UPDATE')
        payload: Event data as dict
        session_id: Optional session identifier
        user_agent: Optional user agent string
        ip_address: Optional IP address
        request_id: Optional request ID
    """
    audit = UMCAuditLog(
        event_type=event_type,
        session_id=session_id,
        payload=payload,
        user_agent=user_agent,
        ip_address=ip_address,
        request_id=request_id,
    )
    db.add(audit)
    db.commit()


if __name__ == "__main__":
    print("UMC Database Module")
    print(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}")
    print()

    print("Testing database connection...")
    health = check_db_health()

    if health["status"] == "healthy":
        print("✅ Database connection healthy")
        print(f"   Latency: {health['latency_ms']}ms")
        print(f"   Sessions: {health['tables']['sessions']}")
        print(f"   Notes: {health['tables']['notes']}")
        print(f"   State Updates: {health['tables']['state_updates']}")
        print(f"   Audit Log: {health['tables']['audit_log']}")
    else:
        print("❌ Database connection failed")
        print(f"   Error: {health['error']}")
