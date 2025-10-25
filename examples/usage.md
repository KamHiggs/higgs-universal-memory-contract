# Higgs Universal Memory Contract — Usage Patterns

This file shows how an assistant using the Higgs Universal Memory Contract (UMC) should behave in common situations.

---

## 1. Establishing Anchors

**User:**  
We’re calling this product “Vibranium Protocol.” The draft deck needs to be ready by November 12, 2025. Tone: no hype, strictly technical and credible.

**Assistant should respond with anchors:**
```text
ANCHOR: Project codename is "Vibranium Protocol".
ANCHOR: Draft investor deck deadline is November 12, 2025.
ANCHOR: Tone must stay direct, technical, and non-hype.
````

The assistant should also produce a `STATE_UPDATE`:

```json
{
  "type": "STATE_UPDATE",
  "session_id": "vibranium-protocol-R1",
  "summary": "We defined the core pitch and deadlines for Vibranium Protocol.",
  "next_steps": [
    "Draft compliance/audit slide",
    "Draft self-host/on-prem slide"
  ],
  "blockers": [
    "Need legal wording for audit claims"
  ],
  "deadline": "2025-11-12"
}
```

---

## 2. Saving Critical Facts to Long-Term Memory

After confirming something matters, the assistant should emit a `SAVE_NOTE`:

```json
{
  "type": "SAVE_NOTE",
  "session_id": "vibranium-protocol-R1",
  "scope": "project",
  "fact": "Deployment must be on-prem / no public cloud allowed.",
  "reason": "This constrains all architecture language and partner strategy."
}
```

Your wrapper code should intercept that and write it to your memory store (DB, vector store, etc.) under that `session_id`.

---

## 3. Requesting Context Instead of Guessing

If the assistant is missing compliance messaging:

```json
{
  "type": "REQUEST_CONTEXT",
  "session_id": "vibranium-protocol-R1",
  "topic": "Latest approved compliance messaging for investor deck"
}
```

Your system should respond in the next prompt by injecting:

```xml
<RETRIEVED_CONTEXT>
Compliance positioning: "Vibranium keeps inference local and logs all decisions in an immutable audit trail suitable for regulated finance and government."
</RETRIEVED_CONTEXT>
```

The assistant must treat `<RETRIEVED_CONTEXT>` as authoritative unless corrected by the user.

---

## 4. Resetting Without Losing the Project

**User:**
`[RESET]`

**Expected assistant behavior:**

1. Clear all temporary working chatter.
2. Keep sticky memory with scope = `permanent` or `project`.
3. Restate what it still knows.

**Assistant response example:**

```text
Context reset complete.

Here's what I am retaining for session_id "vibranium-protocol-R1":
- ANCHOR: Project codename is "Vibranium Protocol".
- ANCHOR: Deadline for draft investor deck is November 12, 2025.
- ANCHOR: Tone is direct, technical, non-hype.
- Sticky requirement: On-prem / no public cloud deployment.

Where would you like to go from here?
```

---

## 5. Handling Corrections / Conflict Resolution

**User:**
Actually, deadline moved. Deck draft is now November 20, 2025.

**Assistant must:**

* Accept user input as source of truth
* Issue updated anchor
* Emit a correctional `SAVE_NOTE`

```text
ANCHOR_UPDATED: The draft investor deck deadline is now November 20, 2025 (was November 12, 2025).
```

```json
{
  "type": "SAVE_NOTE",
  "session_id": "vibranium-protocol-R1",
  "scope": "project",
  "fact": "Deck deadline moved to November 20, 2025.",
  "reason": "Updated delivery expectation from the user; supersedes previous deadline."
}
```

This is how you get auditability. Anyone looking later can see “the deadline moved and we logged it.”

---

## 6. Respecting Privacy / Consent

**User:**
Don’t store this part. This is private: I’m dealing with legal pressure and I’m stressed about it.

**Assistant must NOT emit `SAVE_NOTE` about that detail.**
Instead, it can keep only a high-level reference in working context if needed:

```text
Understood. I will not store this or include details in future summaries.

ANCHOR: The user is under time pressure and needs efficiency and clarity from me.
```

No party names, no case numbers, no direct quotes.
This protects your user and protects you.

---

## 7. New Topic, Same Session

When the user says:
“Switch gears — write the architecture slide,”

The assistant should begin by restating the current state from memory:

```text
Current status for session_id "vibranium-protocol-R1":

- We’re building 'Vibranium Protocol': AI sovereignty + verifiable audit trails.
- Deployment must be on-prem (no public cloud).
- Tone = direct, technical, no hype.
- Draft investor deck deadline: Nov 20, 2025.

Let’s draft the infrastructure / deployment slide with that in mind:
[...assistant continues...]
```

This feels like working with an executive partner instead of starting over every time.
