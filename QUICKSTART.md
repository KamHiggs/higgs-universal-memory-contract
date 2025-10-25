# Quickstart: Run UMC Locally in 5 Minutes

This guide shows how to:
1. Run the UMC Memory Server locally
2. Send it UMC events (`STATE_UPDATE`, `SAVE_NOTE`, `REQUEST_CONTEXT`)
3. Get back `<RETRIEVED_CONTEXT>...</RETRIEVED_CONTEXT>` to feed into your assistant

UMC = "memory infrastructure you control."  
The assistant talks in a standard protocol.  
The middleware stores, retrieves, and audits memory per `session_id`.

---

## 0. Requirements
- Python 3.10+
- pip

No database is required for this minimal reference server.  
(There will be a SQLite-backed version for persistence in production use.)

---

## 1. Install dependencies

From your local machine / virtualenv:

```bash
pip install fastapi uvicorn pydantic
````

This installs the FastAPI app used in `middleware/umc_memory_server.py`.

---

## 2. Run the memory server

From the root of this repo:

```bash
uvicorn middleware.umc_memory_server:app --reload
```

You should now have a server running at:
`http://127.0.0.1:8000`

Test it:

```bash
curl http://127.0.0.1:8000/
```

You should see JSON describing the endpoints:

* `/save_note`
* `/state_update`
* `/request_context`
* `/session/{session_id}/memory`
* `/audit_log`

This means the UMC middleware is up.

---

## 3. Tell the server about a project

Pretend you (or your assistant) are working with a client/project called **Alpha Secure**, and you’re using this session ID:

`alpha-secure-R1`

We’re going to:

1. Send a `STATE_UPDATE` (current status and next steps)
2. Send a `SAVE_NOTE` (sticky constraint that must not be violated)

### 3.1 Send STATE_UPDATE

```bash
curl -X POST http://127.0.0.1:8000/state_update \
  -H "Content-Type: application/json" \
  -d '{
    "type": "STATE_UPDATE",
    "session_id": "alpha-secure-R1",
    "summary": "Defined Alpha Secure positioning and constraints.",
    "next_steps": [
      "Draft compliance positioning slide",
      "Draft sovereignty/on-prem deployment slide"
    ],
    "blockers": [
      "Need legal wording for audit trail claims"
    ],
    "deadline": "2025-11-12"
  }'
```

What this means:

* `summary`: what just got decided / aligned
* `next_steps`: what happens next
* `blockers`: what’s stuck
* `deadline`: high-level milestone

This becomes an auditable timeline of the project.

---

### 3.2 Send SAVE_NOTE

Now we store a sticky constraint for this session.
This is something we MUST respect every time we work on this client.

```bash
curl -X POST http://127.0.0.1:8000/save_note \
  -H "Content-Type: application/json" \
  -d '{
    "type": "SAVE_NOTE",
    "session_id": "alpha-secure-R1",
    "scope": "project",
    "fact": "Deployment must be fully on-prem / no public cloud allowed.",
    "reason": "Affects all infrastructure and compliance messaging."
  }'
```

Notes:

* `scope: "project"` means: keep this for this client/session.
* `"permanent"` would mean "store this long-term across future sessions" (requires user permission).
* `"temporary"` would mean "only matters for this immediate task."

This is how we avoid cross-client leaks. Each client gets their own `session_id`.

---

## 4. Ask for context later (assistant recall without guessing)

Now imagine the assistant is continuing work, maybe hours later, and it doesn't want to hallucinate the compliance story for Alpha Secure. It should NOT guess. It should request memory.

This is done with `REQUEST_CONTEXT`:

```bash
curl -X POST http://127.0.0.1:8000/request_context \
  -H "Content-Type: application/json" \
  -d '{
    "type": "REQUEST_CONTEXT",
    "session_id": "alpha-secure-R1",
    "topic": "Latest compliance positioning and deployment requirements"
  }'
```

Example response (formatted for readability):

```json
{
  "session_id": "alpha-secure-R1",
  "context_block": "<RETRIEVED_CONTEXT>
SESSION_ID: alpha-secure-R1
TOPIC_REQUESTED: Latest compliance positioning and deployment requirements

LATEST_STATE_UPDATE:
- summary: Defined Alpha Secure positioning and constraints.
- next_steps: Draft compliance positioning slide, Draft sovereignty/on-prem deployment slide
- blockers: Need legal wording for audit trail claims
- deadline: 2025-11-12

STICKY_NOTES:
- Deployment must be fully on-prem / no public cloud allowed. (scope=project, reason=Affects all infrastructure and compliance messaging.)
</RETRIEVED_CONTEXT>"
}
```

How to use this:

* Your assistant should literally insert that `<RETRIEVED_CONTEXT> ... </RETRIEVED_CONTEXT>` block into its next prompt before generating the next answer.
* That keeps it aligned with the true state of the project.
* That prevents hallucinating wrong constraints or leaking context from another session.

This is how we get:
**continuity, no guessing, no cross-client bleed.**

---

## 5. Inspect what’s stored for a session (debug / audit)

You can ask the server:
“What do you currently know about session `alpha-secure-R1`?”

```bash
curl http://127.0.0.1:8000/session/alpha-secure-R1/memory
```

You’ll get JSON containing:

* `state_updates`: timeline of big decisions, next steps
* `notes`: sticky memory facts you asked it to store

This is how a human can audit the assistant’s “working memory.”

You can also inspect every event (save / update / retrieval) in the audit log:

```bash
curl http://127.0.0.1:8000/audit_log
```

That’s what compliance teams, regulated orgs, and multi-client agencies care about.

---

## 6. Hooking this up to a real assistant (Claude, GPT, local, etc.)

You now have two halves:

1. The assistant
2. The memory server

### Assistant side:

Give your model the system prompt in
`prompts/umc_system_prompt.md`.

That prompt teaches it to:

* Emit `STATE_UPDATE` after important decisions
* Emit `SAVE_NOTE` when something matters long-term
* Emit `REQUEST_CONTEXT` instead of guessing
* Respect "do not store this" and never leak across `session_id`s

### Memory server side:

* Receives those JSON blocks via `/state_update`, `/save_note`, `/request_context`
* Returns `<RETRIEVED_CONTEXT>...</RETRIEVED_CONTEXT>` blocks on demand
* Keeps an audit trail by `session_id`

This separation is the whole point:

* The assistant does not get to hoard memory silently.
* The org / user actually owns the memory.

---

## 7. Production notes

This reference server keeps everything in memory (Python dicts).
For production you will likely want:

* A persisted store (SQLite, Postgres, etc.)
* API auth / keys
* Optional vector search for semantic recall
* Retention rules for `"temporary"` scope
* Per-session isolation guarantees for multi-client teams

Those are the next milestones in this repo.

---

## Summary

UMC gives you:

* Project-scoped recall (`session_id`)
* Consent-aware retention (`scope`)
* Auditable snapshots of state (`STATE_UPDATE`)
* Safe “please remember this” requests (`SAVE_NOTE`)
* Safe “please remind me” requests (`REQUEST_CONTEXT`)
* `<RETRIEVED_CONTEXT>` blocks you can feed right back into the model

It’s memory infrastructure you control — not memory locked inside a vendor.
