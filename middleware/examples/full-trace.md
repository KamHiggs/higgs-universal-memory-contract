# Full Multi-Turn Trace (UMC in Action)

This example shows:
- An assistant working with two separate clients / projects
- No data leak between them
- How STATE_UPDATE, SAVE_NOTE, REQUEST_CONTEXT are used
- How the middleware responds

We'll pretend the assistant is backed by the UMC middleware in `middleware/umc_memory_server.py`.

---

## 1. User kicks off Project A

**User (session_id = "alpha-secure-R1"):**  
We’re building "Alpha Secure". It's a compliance-focused AI assistant for finance clients.  
Deadline for first investor deck draft is November 12, 2025.  
Tone needs to stay direct and credible, no hype.  
Also: deployment must be on-prem. No public cloud, at all.

**Assistant response (to user):**
```text
ANCHOR: Project codename is "Alpha Secure".
ANCHOR: Draft investor deck deadline is November 12, 2025.
ANCHOR: Tone must stay direct, credible, and non-hype.
ANCHOR: Deployment must be on-prem (no public cloud allowed).
````

**Assistant also emits STATE_UPDATE (to middleware via /state_update):**

```json
{
  "type": "STATE_UPDATE",
  "session_id": "alpha-secure-R1",
  "summary": "Defined core pitch and delivery constraints for Alpha Secure.",
  "next_steps": [
    "Draft compliance positioning slide",
    "Draft on-prem / sovereignty slide"
  ],
  "blockers": [
    "Need legal wording for audit trail claims"
  ],
  "deadline": "2025-11-12"
}
```

**Assistant also emits SAVE_NOTE (to middleware via /save_note):**

```json
{
  "type": "SAVE_NOTE",
  "session_id": "alpha-secure-R1",
  "scope": "project",
  "fact": "Deployment must be fully on-prem / no public cloud allowed.",
  "reason": "Affects all infrastructure and compliance messaging."
}
```

The middleware stores both the STATE_UPDATE timeline and the sticky requirement ("on-prem only") for `alpha-secure-R1`.

---

## 2. Later, same user switches to Project B (new client)

**User (session_id = "orion-health-R2"):**
New project. We’re calling it "Orion Health Vault." This one's for healthcare compliance.
Different rules: we *can* use a managed cloud as long as it's HIPAA compliant.
Tone is reassuring / protective, not aggressive. Deadline is December 1.

**Assistant response (to user):**

```text
ANCHOR: Project codename is "Orion Health Vault".
ANCHOR: Draft deck deadline is December 1, 2025.
ANCHOR: Tone should be reassuring and protective.
ANCHOR: Cloud deployment is allowed if HIPAA compliant.
```

**Assistant emits STATE_UPDATE to middleware (/state_update):**

```json
{
  "type": "STATE_UPDATE",
  "session_id": "orion-health-R2",
  "summary": "Captured Orion Health Vault positioning, tone guidelines, and deployment rules.",
  "next_steps": [
    "Draft patient privacy slide",
    "Draft HIPAA-compliant architecture slide"
  ],
  "blockers": [],
  "deadline": "2025-12-01"
}
```

**Assistant emits SAVE_NOTE to middleware (/save_note):**

```json
{
  "type": "SAVE_NOTE",
  "session_id": "orion-health-R2",
  "scope": "project",
  "fact": "Cloud deployment is allowed if HIPAA compliant.",
  "reason": "Impacts infrastructure messaging and trust framing."
}
```

Notice:

* `alpha-secure-R1` says “on-prem only”
* `orion-health-R2` explicitly allows compliant cloud
* These are *opposite requirements*
* UMC isolates them cleanly using `session_id`

No cross-pollution. No leak.

---

## 3. Assistant needs to continue work on Alpha Secure later

The assistant doesn’t want to hallucinate messaging. It asks the middleware for context:

**Assistant → middleware (/request_context):**

```json
{
  "type": "REQUEST_CONTEXT",
  "session_id": "alpha-secure-R1",
  "topic": "Latest compliance positioning and deployment requirements"
}
```

**Middleware responds (to assistant) with:**

```json
{
  "session_id": "alpha-secure-R1",
  "context_block": "<RETRIEVED_CONTEXT>\nSESSION_ID: alpha-secure-R1\nTOPIC_REQUESTED: Latest compliance positioning and deployment requirements\n\nLATEST_STATE_UPDATE:\n- summary: Defined core pitch and delivery constraints for Alpha Secure.\n- next_steps: Draft compliance positioning slide, Draft on-prem / sovereignty slide\n- blockers: Need legal wording for audit trail claims\n- deadline: 2025-11-12\n\nSTICKY_NOTES:\n- Deployment must be fully on-prem / no public cloud allowed. (scope=project, reason=Affects all infrastructure and compliance messaging.)\n</RETRIEVED_CONTEXT>"
}
```

**Assistant now continues to the user with perfect recall, without guessing:**

```text
Here's the current positioning for Alpha Secure:

- This platform is built for regulated finance clients.
- Deployment is strictly on-prem. No public cloud use is permitted.
- The story is "AI sovereignty + verifiable audit trails," but we still need final legal language on the audit trail claims.

I can draft the Sovereignty / Compliance slide now using that framing. Want me to do that?
```

That is UMC in motion:

* Audit trail captured
* Session isolation enforced
* Recall without hallucination
* No accidental reuse of Orion Health Vault's HIPAA/cloud policy in Alpha Secure's pitch

This is exactly how agencies, consultants, and internal AI “chief of staff” assistants avoid leaking client A → client B.
