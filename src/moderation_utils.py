"""
SOMA Thalamus Module (moderation_utils.py)

Acts as the central relay and analytical brain. This module determines 
if content meets safety criteria by loading policies from a YAML file 
and routing decisions via System 1 or System 2.
"""

import yaml
import os
from typing import Dict, Any

class SomaEngine:
    """
    The Thalamus of the SOMA system.
    
    It evaluates incoming 'sensory' data (text) against established 
    safety policies and determines the confidence of a pass/fail decision.
    """

    def __init__(self, config_path: str = "configs/policy.yaml"):
        """
        Initializes the engine by loading the 'Source of Truth' from the config folder.
        
        Args:
            config_path (str): Path to the YAML policy file.
        """
        # Load the policy from your configs folder
        try:
            # We use absolute pathing logic to ensure it finds the file 
            # regardless of where you run the script from.
            with open(config_path, 'r') as f:
                self.policy = yaml.safe_load(f)
            
            # Extract values from your specific YAML structure
            tox_config = self.policy.get('categories', {}).get('hate_speech', {})
            self.threshold = tox_config.get('base_threshold', 0.7)
            self.window = tox_config.get('gray_zone_window', 0.15)
            self.blocked_keywords = self.policy.get('keywords', [])
            
        except FileNotFoundError:
            print(f"CRITICAL ERROR: Configuration file not found at {config_path}")
            # Fallback defaults so the system doesn't crash during testing
            self.threshold = 0.7
            self.window = 0.15
            self.blocked_keywords = ["bad", "unsafe", "error"]

    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text and routes it to a cognitive system path based on 
        the thresholds defined in policy.yaml.

        Logic:
        1. Calculate a raw score based on keyword matches.
        2. Check if the score falls into the 'Cognitive Gray Zone'.
        3. Assign a path: System 1 (Reflexive) or System 2 (Deliberative).
        """
        text_lower = text.lower()
        
        # Simulating a model score: 
        # We start at 1.0 (perfectly safe) and subtract for every violation.
        matches = [word for word in self.blocked_keywords if word in text_lower]
        
        # Each 'bad' word reduces safety by 0.3
        raw_score = max(0.0, 1.0 - (len(matches) * 0.3))

        # Determine the Cognitive Path
        # The 'Gray Zone' is the area around the threshold where we aren't 100% sure.
        lower_bound = self.threshold - self.window
        upper_bound = self.threshold + self.window
        
        is_ambiguous = lower_bound <= raw_score <= upper_bound
        
        if is_ambiguous:
            path = "System 2"
            decision = "RESERVED (HITL)"
            rationale = f"Ambiguous signal: Score {raw_score:.2f} is within the Gray Zone ({lower_bound:.2f}-{upper_bound:.2f})."
        else:
            path = "System 1"
            decision = "PASS" if raw_score >= self.threshold else "FAIL"
            rationale = f"High-confidence {decision} based on safety threshold."

        return {
            "score": round(raw_score, 2),
            "decision": decision,
            "path": path,
            "rationale": rationale,
            "metadata": {
                "keywords_found": matches,
                "policy_threshold": self.threshold
            }
        }

# --- Quick Test Loop ---
if __name__ == "__main__":
    engine = SomaEngine()
    # Test a clear 'PASS'
    print(engine.evaluate("This is a lovely morning!"))
    # Test a 'Gray Zone' or 'FAIL'
    print(engine.evaluate("This text is bad and unsafe."))