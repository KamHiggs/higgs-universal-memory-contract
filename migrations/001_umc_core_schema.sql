-- ============================================================================
-- Universal Memory Contract (UMC) Core Schema
-- ============================================================================
--
-- PURPOSE: Session-scoped episodic memory storage for AI assistants
--
-- TABLES:
-- - umc_sessions: Session registry and metadata
-- - umc_notes: SAVE_NOTE events (sticky memory)
-- - umc_state_updates: STATE_UPDATE events (decision timeline)
-- - umc_audit_log: Complete audit trail of all UMC events
--
-- PRIVACY:
-- - Session-scoped (no cross-session leakage)
-- - Retention policies enforced at query time
-- - PII detection flags for manual review
-- - Audit trail for compliance
--
-- ============================================================================

-- ============================================================================
-- 1. SESSIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS umc_sessions (
  id BIGSERIAL PRIMARY KEY,

  -- Session identity
  session_id TEXT NOT NULL UNIQUE,

  -- Metadata
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Context
  user_id TEXT,
  assistant_id TEXT,
  project_id TEXT,

  -- Lifecycle
  status TEXT NOT NULL DEFAULT 'active', -- 'active', 'archived', 'deleted'
  retention_policy TEXT DEFAULT 'standard', -- 'standard', 'extended', 'permanent'
  expires_at TIMESTAMPTZ,

  -- Stats (updated by triggers)
  note_count INT DEFAULT 0,
  state_update_count INT DEFAULT 0,
  last_note_at TIMESTAMPTZ,
  last_state_update_at TIMESTAMPTZ
);

CREATE INDEX idx_umc_sessions_session_id ON umc_sessions(session_id);
CREATE INDEX idx_umc_sessions_status ON umc_sessions(status);
CREATE INDEX idx_umc_sessions_expires_at ON umc_sessions(expires_at);
CREATE INDEX idx_umc_sessions_last_activity ON umc_sessions(last_activity_at DESC);

COMMENT ON TABLE umc_sessions IS 'Registry of all UMC sessions with metadata and lifecycle tracking';


-- ============================================================================
-- 2. NOTES (SAVE_NOTE events)
-- ============================================================================

CREATE TABLE IF NOT EXISTS umc_notes (
  id BIGSERIAL PRIMARY KEY,

  -- Session scope
  session_id TEXT NOT NULL,

  -- UMC SAVE_NOTE fields
  type TEXT NOT NULL DEFAULT 'SAVE_NOTE',
  scope TEXT NOT NULL, -- 'permanent', 'project', 'temporary'
  fact TEXT NOT NULL,
  reason TEXT NOT NULL,

  -- Metadata
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Privacy & compliance
  rejected BOOLEAN DEFAULT FALSE,
  rejected_reason TEXT,
  contains_pii BOOLEAN DEFAULT FALSE, -- Flagged for review
  redacted BOOLEAN DEFAULT FALSE,

  -- Lifecycle
  deleted_at TIMESTAMPTZ,

  -- Full text search
  fact_search TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', fact)) STORED
);

CREATE INDEX idx_umc_notes_session_id ON umc_notes(session_id);
CREATE INDEX idx_umc_notes_scope ON umc_notes(scope);
CREATE INDEX idx_umc_notes_timestamp ON umc_notes(timestamp DESC);
CREATE INDEX idx_umc_notes_rejected ON umc_notes(rejected) WHERE rejected = FALSE;
CREATE INDEX idx_umc_notes_search ON umc_notes USING GIN(fact_search);

COMMENT ON TABLE umc_notes IS 'SAVE_NOTE events - sticky memory facts persisted by assistant';
COMMENT ON COLUMN umc_notes.scope IS 'Memory scope: permanent (survive session end), project (project lifetime), temporary (session only)';
COMMENT ON COLUMN umc_notes.rejected IS 'TRUE if note was rejected due to sensitive content (password, SSN, etc.)';
COMMENT ON COLUMN umc_notes.contains_pii IS 'Flagged for manual review if PII detected';


-- ============================================================================
-- 3. STATE UPDATES (STATE_UPDATE events)
-- ============================================================================

CREATE TABLE IF NOT EXISTS umc_state_updates (
  id BIGSERIAL PRIMARY KEY,

  -- Session scope
  session_id TEXT NOT NULL,

  -- UMC STATE_UPDATE fields
  type TEXT NOT NULL DEFAULT 'STATE_UPDATE',
  summary TEXT NOT NULL,
  next_steps JSONB NOT NULL DEFAULT '[]', -- Array of strings
  blockers JSONB NOT NULL DEFAULT '[]', -- Array of strings
  deadline TEXT,

  -- Metadata
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Lifecycle
  superseded_by_id BIGINT, -- Pointer to newer state update
  is_current BOOLEAN DEFAULT TRUE -- Only latest state update per session
);

CREATE INDEX idx_umc_state_updates_session_id ON umc_state_updates(session_id);
CREATE INDEX idx_umc_state_updates_timestamp ON umc_state_updates(timestamp DESC);
CREATE INDEX idx_umc_state_updates_current ON umc_state_updates(session_id, is_current) WHERE is_current = TRUE;

COMMENT ON TABLE umc_state_updates IS 'STATE_UPDATE events - timeline of decisions, next steps, blockers';
COMMENT ON COLUMN umc_state_updates.is_current IS 'TRUE for the most recent state update in this session';


-- ============================================================================
-- 4. AUDIT LOG
-- ============================================================================

CREATE TABLE IF NOT EXISTS umc_audit_log (
  id BIGSERIAL PRIMARY KEY,

  -- Event identity
  event_type TEXT NOT NULL, -- 'SAVE_NOTE', 'STATE_UPDATE', 'REQUEST_CONTEXT', 'DELETE_SESSION', etc.
  session_id TEXT,

  -- Event data
  payload JSONB NOT NULL,

  -- Metadata
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Request context
  user_agent TEXT,
  ip_address INET,
  request_id TEXT
);

CREATE INDEX idx_umc_audit_log_session_id ON umc_audit_log(session_id);
CREATE INDEX idx_umc_audit_log_event_type ON umc_audit_log(event_type);
CREATE INDEX idx_umc_audit_log_timestamp ON umc_audit_log(timestamp DESC);

COMMENT ON TABLE umc_audit_log IS 'Complete audit trail of all UMC events for compliance and debugging';


-- ============================================================================
-- 5. TRIGGERS (Auto-update session stats)
-- ============================================================================

-- Update session last_activity_at on any event
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE umc_sessions
  SET last_activity_at = NEW.timestamp
  WHERE session_id = NEW.session_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_note_updates_session_activity
  AFTER INSERT ON umc_notes
  FOR EACH ROW
  EXECUTE FUNCTION update_session_activity();

CREATE TRIGGER trigger_state_update_updates_session_activity
  AFTER INSERT ON umc_state_updates
  FOR EACH ROW
  EXECUTE FUNCTION update_session_activity();


-- Update session note_count
CREATE OR REPLACE FUNCTION update_session_note_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE umc_sessions
  SET note_count = note_count + 1,
      last_note_at = NEW.timestamp
  WHERE session_id = NEW.session_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_note_count
  AFTER INSERT ON umc_notes
  FOR EACH ROW
  EXECUTE FUNCTION update_session_note_count();


-- Update session state_update_count
CREATE OR REPLACE FUNCTION update_session_state_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE umc_sessions
  SET state_update_count = state_update_count + 1,
      last_state_update_at = NEW.timestamp
  WHERE session_id = NEW.session_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_state_update_count
  AFTER INSERT ON umc_state_updates
  FOR EACH ROW
  EXECUTE FUNCTION update_session_state_count();


-- Mark old state updates as superseded
CREATE OR REPLACE FUNCTION supersede_old_state_updates()
RETURNS TRIGGER AS $$
BEGIN
  -- Mark all previous state updates for this session as not current
  UPDATE umc_state_updates
  SET is_current = FALSE,
      superseded_by_id = NEW.id
  WHERE session_id = NEW.session_id
    AND id != NEW.id
    AND is_current = TRUE;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_supersede_state_updates
  AFTER INSERT ON umc_state_updates
  FOR EACH ROW
  EXECUTE FUNCTION supersede_old_state_updates();


-- ============================================================================
-- 6. UTILITY FUNCTIONS
-- ============================================================================

-- Get current state for a session
CREATE OR REPLACE FUNCTION get_current_state(p_session_id TEXT)
RETURNS TABLE(
  summary TEXT,
  next_steps JSONB,
  blockers JSONB,
  deadline TEXT,
  timestamp TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    su.summary,
    su.next_steps,
    su.blockers,
    su.deadline,
    su.timestamp
  FROM umc_state_updates su
  WHERE su.session_id = p_session_id
    AND su.is_current = TRUE
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_state IS 'Get the current state update for a session';


-- Get all active notes for a session
CREATE OR REPLACE FUNCTION get_session_notes(p_session_id TEXT)
RETURNS TABLE(
  fact TEXT,
  scope TEXT,
  reason TEXT,
  timestamp TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    n.fact,
    n.scope,
    n.reason,
    n.timestamp
  FROM umc_notes n
  WHERE n.session_id = p_session_id
    AND n.rejected = FALSE
    AND n.deleted_at IS NULL
  ORDER BY n.timestamp DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_session_notes IS 'Get all active (non-rejected, non-deleted) notes for a session';


-- ============================================================================
-- 7. RETENTION POLICY (Cleanup old sessions)
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INT AS $$
DECLARE
  deleted_count INT;
BEGIN
  -- Mark expired sessions as deleted
  WITH updated AS (
    UPDATE umc_sessions
    SET status = 'deleted'
    WHERE status = 'active'
      AND expires_at IS NOT NULL
      AND expires_at < NOW()
    RETURNING id
  )
  SELECT COUNT(*) INTO deleted_count FROM updated;

  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_sessions IS 'Mark expired sessions as deleted (call this periodically via cron)';


-- ============================================================================
-- 8. INITIAL DATA (for testing)
-- ============================================================================

-- Insert a test session
INSERT INTO umc_sessions (session_id, user_id, assistant_id, project_id)
VALUES ('test-session-001', 'test-user', 'claude-sonnet-4-5', 'umc-integration-test')
ON CONFLICT (session_id) DO NOTHING;

COMMENT ON TABLE umc_sessions IS 'Test session created for validation';
