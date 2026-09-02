"""
SOMA Memory Module.

This module provides the core logic for recording system events. 
It acts as the system's 'memory' by converting live decisions 
into a structured, persistent format (JSON).
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SomaLogger:
    """
    Acts as the Memory Core of the SOMA system.

    The logic here ensures that every decision is captured in a durable, 
    machine-readable format. This creates an audit trail that allows the 
    system's reasoning to be reviewed and analyzed by auditors later.
    """

    def __init__(self, log_dir: str = "logs", log_file: str = "soma_audit.log"):
        """
        Initializes the environment for the memory core.

        Follows a 'defensive' pattern: verifies the directory exists before 
        attempting to write, preventing runtime path errors.

        Args:
            log_dir (str): The directory where logs are stored.
            log_file (str): The filename for the JSON audit trail.
        """
        # Ensure the log directory exists (Defensive Engineering)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_path = os.path.join(log_dir, log_file)
        
        # Configure the logging framework
        # 'force=True' ensures settings update even if the cell is re-run in Jupyter
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(message)s',
            force=True
        )
        self.logger = logging.getLogger("SomaLogger")

    def log_decision(
        self, 
        module_name: str, 
        decision: str, 
        rationale: str,
        cognitive_system: str = "System 1",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Translates a system decision into a structured JSON event.

        By keeping 'metadata' as a nested dictionary, we ensure the system 
        is 'future-proof'—we can add new data points to the metadata 
        without breaking the core log structure.

        Args:
            module_name (str): The system component (e.g., 'Arbiter').
            decision (str): The final action taken (e.g., 'BLOCK', 'APPROVE').
            rationale (str): The 'human-readable' explanation for the decision.
            cognitive_system (str): Identifies if the path was 'System 1' 
                (Reflexive) or 'System 2' (Deliberative/Gray Zone).
            metadata (dict, optional): Catch-all for scores, text, or model IDs.
        """
        
        # Construct the 'Audit Envelope'
        log_entry = {
            "timestamp": datetime.now().isoformat(),  # ISO 8601 Standard
            "module": module_name,
            "cognitive_system": cognitive_system,
            "decision": decision,
            "rationale": rationale,
            "metadata": metadata or {}  # The 'Payload' bucket
        }
        
        # Serialize the state to a single-line JSON string for the log file
        self.logger.info(json.dumps(log_entry))

# --- Testing Block ---
if __name__ == "__main__":
    # Quick verification that the 'Memory' is working correctly
    test_logger = SomaLogger()
    test_logger.log_decision(
        module_name="Test_Arbiter",
        decision="ALLOW",
        rationale="Score was significantly below toxicity threshold.",
        cognitive_system="System 1",
        metadata={"score": 0.12, "text_length": 45}
    )
    print(f"Log successfully committed to: {test_logger.log_path}")