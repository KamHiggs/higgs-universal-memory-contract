# Higgs Universal Memory Contract (UMC)
Version: v0.9-core  
Status: Draft-Stable  

## Get Started Fast

- **Run it locally in 5 minutes:**  
  See [QUICKSTART.md](./QUICKSTART.md) for how to launch the UMC memory server with FastAPI, send it `STATE_UPDATE` / `SAVE_NOTE`, and retrieve `<RETRIEVED_CONTEXT>...</RETRIEVED_CONTEXT>` with curl.

- **Make your AI speak UMC natively:**  
  See [prompts/umc_system_prompt.md](./prompts/umc_system_prompt.md) for the system prompt that teaches any assistant (Claude, GPT, local models, etc.) to:  
  - emit `STATE_UPDATE` and `SAVE_NOTE` after important decisions  
  - call `REQUEST_CONTEXT` instead of guessing  
  - respect `session_id` boundaries and “do not store this”

- **Reference middleware (memory you control):**  
  See [middleware/umc_memory_server.py](./middleware/umc_memory_server.py) for the lightweight FastAPI server that:  
  - stores project-scoped memory by `session_id`  
  - returns `<RETRIEVED_CONTEXT>` blocks on request  
  - keeps an audit trail of what was decided, when, and why  

UMC is memory infrastructure you control — not memory locked inside a vendor.



Maintainers: Kamden Higgs • Higgs AI

## What This Is
The Higgs Universal Memory Contract (UMC) is an open, model-agnostic memory protocol for AI assistants and agent systems.

It defines:
- What should be remembered
- What should **never** be remembered
- How memory is summarized and updated over time
- How to cleanly hand off state between different agents or sessions
- How to prevent cross-project leakage and compliance disasters

In plain terms:  
**It gives AI an executive memory with boundaries.**

## Why This Exists
Most assistants today either:
- forget everything (painful),  
- or remember everything (dangerous).

UMC gives you controlled, auditable, scoped memory:
- Project-scoped recall instead of one giant “user profile dump”
- Explicit consent and redaction rules
- Machine-readable handoff signals that any agent can use
- A way to resume work midstream without rereading 200 pages of chat

UMC is designed for:
- founders
- operators
- consultants with multiple clients
- multi-agent systems
- compliance-heavy environments

This is not just for “chat.”  
This is for running an AI-driven operation.

---

## Core Concepts

### `session_id`
Every project / engagement / initiative must have a `session_id`.  
All memory is tagged with this.  
That prevents data bleeding across clients or contexts.

Example:  
`session_id: "vibranium-protocol-R1"`

### Sticky Memory
Information that must survive topic switches and future turns:
- goals and success criteria
- constraints and non-negotiables
- milestones / deadlines
- user tone / formatting preferences
- current state of the project

Sticky memory is protected. It is never thrown away unless the user explicitly says it changed.

### Working Memory
Recent, local conversation context. Ephemeral.  
We only keep the most recent 8 turns verbatim; everything older gets summarized.

### Anchors
When a fact becomes stable, it is restated as:
`ANCHOR: <fact>`

Anchors are carried forward in summaries and cannot be silently changed.  
If reality changes (like deadlines move), we generate `ANCHOR_UPDATED:` and log the correction.

### STATE_UPDATE
After every major decision, delivery, or shift in direction, the assistant produces a `STATE_UPDATE` block:
- What we decided
- What’s next
- Blockers
- Deadlines

This becomes the “living project status.”

### SAVE_NOTE
When something needs to go into long-term memory, the assistant emits a `SAVE_NOTE` object asking the host system to persist it.

The note includes:
- `session_id`
- `scope` (permanent | project | temporary)
- The fact
- Why it matters

### REQUEST_CONTEXT
When the assistant is missing something important (like the last approved pitch language), it doesn’t hallucinate.  
It emits a `REQUEST_CONTEXT` object telling the host system exactly what it needs retrieved.

---

## Privacy and Safety
UMC explicitly forbids storing:
- passwords, keys, auth tokens
- financial instrument numbers
- government IDs
- medical/diagnostic detail unless the user consents
- raw legal text or contracts unless the user consents

Sensitive things are summarized at a high level:
> “The user has an outstanding legal deadline mid-November”  
NOT  
> “The user is being sued by X in case #12345 in Los Angeles Superior Court”

If the user says “do not store this,” “off the record,” or “PRIVATE,”  
the assistant must not emit `SAVE_NOTE` for that content.

This builds trust for enterprise and also protects you from cross-client leak risk.

---

## Memory Flow
```text
User ↔ Assistant
        ↓
    STATE_UPDATE  (project status snapshot)
        ↓
    SAVE_NOTE     (assistant asks host to persist critical facts)
        ↓
 Long-term Memory Store (DB, vector store, disk, etc.)
        ↓
  REQUEST_CONTEXT (assistant asks host to retrieve what it needs)
        ↓
   <RETRIEVED_CONTEXT> block feeds back into assistant

---

## Contact / Attribution

**Higgs Universal Memory Contract (UMC)**  
Created by Kamden Higgs • Higgs AI

UMC is an open, model-agnostic memory protocol for AI assistants and agent systems.  
It defines session-scoped memory (`session_id`), consent-aware retention (`scope`: permanent | project | temporary), and machine-readable handoff signals (`STATE_UPDATE`, `SAVE_NOTE`, `REQUEST_CONTEXT`) to prevent cross-client data leaks and create auditable AI behavior.

This work is published under the Apache 2.0 License.

If you're implementing UMC in assistants, multi-agent workflows, or enterprise environments and want to align on interoperability or governance, reach out.
