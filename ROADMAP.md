# Higgs Universal Memory Contract — Roadmap

## v1.0 Goals
These are the upgrades planned after v0.9-core.

### 1. Scoped Retention Timers
- Add `expires_at` or `ttl` for `scope: "temporary"`.
- Behavior: Your memory layer should auto-drop these notes after task completion or a set duration.

### 2. Cross-Project Sharing Rules
- Add a `share_across_sessions` flag.
- Default: `false`.
- Only if the user explicitly says “you may reuse this across my other work,” set it `true`.
- This prevents accidental leakage between clients or products.

### 3. Admin / Audit Trail
- Formalize an append-only log of:
  - Every `STATE_UPDATE`
  - Every `SAVE_NOTE`
  - Every `ANCHOR_UPDATED`
- Include timestamps and attribution (`assistant`, `user`, or `system`).
- This is crucial for regulated sectors (finance, gov, health).

### 4. Compliance Hooks
- Pluggable redaction layer before persistence.
- Example: strip emails, phone numbers, secrets, SSNs before `SAVE_NOTE` is written to disk.

### 5. Middleware Reference Implementation
- Minimal open-source service that:
  - Listens for `SAVE_NOTE` / `REQUEST_CONTEXT` in assistant output
  - Stores / retrieves notes by `session_id`
  - Injects `<RETRIEVED_CONTEXT>...</RETRIEVED_CONTEXT>` blocks back into the model

This lets teams adopt UMC without building all the plumbing from scratch.

---

## Enterprise Extensions (Planned)
These features are intended for high-trust / high-liability deployments.

1. **Org Retention Policy**
   - Central policy file that defines what categories may be kept permanently.
   - Example: `"legal_details": "never"`, `"tone_preferences": "always"`.
   - Assistant should respect this automatically.

2. **Discovery / Export Mode**
   - Export all `STATE_UPDATE` + anchors + timeline for a given `session_id`.
   - Useful for legal review, investor updates, SOC2 evidence, etc.

3. **Role-Based Context Access**
   - Multiple assistants in the same org.
   - Each assistant can `REQUEST_CONTEXT` only for memory scopes it's allowed to see.
   - Example: Finance agent can’t pull product IP notes without clearance.

---

## Long-Term Vision
The Higgs Universal Memory Contract becomes:
- A standard way assistants ask for recall and store decisions
- A portable memory layer that isn’t owned by any single vendor
- An auditable trail of “what was decided, when, and why,” so teams can trust AI to actually run work

This is not prompt engineering.
This is operational memory governance.
