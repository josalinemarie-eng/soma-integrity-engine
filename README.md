# Soma: Integrity Engine

Soma is a decision-making engine for AI moderation. It acts as the central processor for platform safety, translating raw model probability into actionable safety decisions.

## The Evolution of the Project
This project represents the second iteration of my safety architecture.

* **Phase I (The Reflex Arc):** I began by exploring simple, automated responses—a "reflex"—where high-confidence model output triggered an immediate action. It was fast and efficient, but lacked the complexity needed for nuanced policy enforcement.
* **Phase II (Soma):** As my requirements grew, I realized I needed more than a reflex; I needed a processing center. I moved from the Reflex Arc to the **Soma**—the "cell body" of the neuron. Just as a biological soma integrates incoming signals from dendrites to decide whether to fire a response, this engine integrates incoming AI data to determine the correct safety action.

## How It Works: The Soma Metaphor
In a biological neuron, the **soma** is the metabolic core where the decision to "fire" is made. My engine performs the same function:

1.  **Dendrites (Input):** The engine receives inference probabilities from the AI model.
2.  **Soma (Processing):** The engine applies business logic, policy thresholds, and audit requirements to the data. It weighs the uncertainty.
3.  **Axon (Action):** The engine executes the final decision—Approve, Escalate, or Block.

By decoupling the "processing" (Soma) from the "perception" (the AI model), I can update safety rules, thresholds, and audit logic without needing to retrain or modify the underlying machine learning models.

## Getting Started

```python
from src.integrity_engine import IntegrityEngine

# 1. Initialize the Soma engine with safety thresholds
# The engine processes the input signal to determine the output action
soma = IntegrityEngine(auto_approve_threshold=0.85, review_threshold=0.50)

# 2. Process content signals
decision = soma.adjudicate(content_id="post_123", probability=0.65)

# Output: 
# [AUDIT] {'content_id': 'post_123', 'action': 'REVIEW', 'reason': 'Ambiguity threshold met'}
