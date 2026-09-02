# Soma: Integrity Engine

Soma is a context-aware decision engine for AI moderation. It acts as the central processor for platform safety, decoupling raw model probabilities from policy execution to turn uncertain ML outputs into deterministic, auditable safety decisions.

## The Evolution of the Project

This project represents the second iteration of my safety architecture, moving from basic automated triggers to central processing logic:

* **Phase I (The Reflex Arc):** I started with simple, automated responses—a "reflex"—where high-confidence model outputs triggered immediate actions. It was fast and low-latency, but failed when handling nuanced, ambiguous policy edge cases.
* **Phase II (Soma):** To handle real-world policy complexity, I expanded beyond a reflex to build a central processing engine. Named after the biological *soma* (the cell body of a neuron that integrates incoming dendritic signals before firing), this engine aggregates incoming model probabilities, policy logic, and uncertainty thresholds to determine the final safety action.

## How It Works: The Soma Metaphor

I approach safety design by mapping biological signal processing directly to software architecture:

1. **Dendrites (Input):** Receives raw inference probabilities and context signals from upstream models.
2. **Soma (Processing):** Applies business logic, policy thresholds, and audit rules while actively weighing model uncertainty.
3. **Axon (Action):** Triggers the final executable decision—`Approve`, `Escalate`, or `Block`.

## System Interface & Data Flow

The Soma engine acts as a middleware abstraction layer. It consumes inference signals, applies dynamic threshold parameters, and outputs structured audit records.

```
[ Raw Model Output ] ---> ( Dendrites: Signal Input )
│
▼
( Soma: Policy & Risk )
- Auto-Approve (p >= 0.85)
- Ambiguity Zone (0.50 <= p < 0.85)
- Auto-Block   (p < 0.50)
│
▼
[ Auditable Action ] <--- ( Axon: Decision Router )
```
### Example Adjudication

```python
# 1. Initialize the Soma engine with safety thresholds
soma = IntegrityEngine(auto_approve_threshold=0.85, review_threshold=0.50)

# 2. Process content signals
decision = soma.adjudicate(content_id="post_123", probability=0.65)
```

JSON
```
{
  "content_id": "post_123",
  "model_probability": 0.65,
  "adjudication": "REVIEW",
  "policy_version": "v2.1",
  "reason": "Ambiguity threshold met (0.50 <= p < 0.85)",
  "timestamp": "2026-09-02T13:35:00Z"
}
```
Core Architectural Principles
Decoupled Logic: Keeps raw ML predictions separate from business policy so thresholds update dynamically without needing to retrain base models.
Explainability & Auditability (XAI): Produces structured, deterministic logs for every adjudication to maintain clear audit trails for compliance.
Uncertainty Management: Captures model ambiguity in middle-band score zones, routing edge cases to human-in-the-loop (HITL) review processes.
