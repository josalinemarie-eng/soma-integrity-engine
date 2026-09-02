import json
import logging
import html
import re
from typing import Dict, List, Any, Optional

# Configure logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataHandler:
    """
    The intake gateway for the SOMA moderation system or the "sensory intake".

    This class handles the retrieval, sanitization, and verification of 
    incoming data. It acts as a security firewall, ensuring that only clean, 
    properly formatted information enters the cognitive pipeline, preventing 
    injection attacks or malformed data errors.

    Theory: Acts as the system's sensory filter, retrieving raw information and stripping 
    away "noise" like HTML tags to ensure a clean signal. It performs a rigorous 
    "Gatekeeper" check to verify that the data structure is complete and safe. 
    This ensures the SOMA Engine only processes high-quality, valid data, 
    preventing expensive errors or security vulnerabilities downstream.

    Attributes:
        source_config (Dict[str, Any]): Configuration dict for data sources 
            (e.g., database credentials, bucket paths).
    """

    def __init__(self, source_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the data handler with the necessary connection settings.

        Args:
            source_config (Dict[str, Any]): Configuration dict for data sources.
        """
        self.source_config = source_config or {}

    def ingest_registry(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Ingests a SOMA JSONL registry and repairs malformed entries.
        
        This method resolves structural inconsistencies (the "Missing 25" problem)
        by implementing a resilient healing loop for string-wrapped JSON and 
        hidden encoding characters.

        Args:
            file_path (str): The path to the .jsonl registry file.

        Returns:
            List[Dict[str, Any]]: A list of sanitized and validated compounds.
        """
        sanitized_compounds = []
        failures = 0

        try:
            # 'utf-8-sig' handles invisible Byte Order Marks that cause decode errors
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                for line_num, line in enumerate(f, 1):
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    
                    try:
                        # Stage 1: Standard JSON decoding
                        data = json.loads(clean_line)
                        
                        # Stage 2: Normalization for string-wrapped JSON
                        if isinstance(data, str):
                            data = json.loads(data)
                        
                        # Stage 3: Sensory Sanitization
                        clean_data = self.sanitize(data)
                        
                        # Stage 4: Gatekeeper Validation
                        if self.validate_schema(clean_data):
                            sanitized_compounds.append(clean_data)
                        else:
                            failures += 1

                    except json.JSONDecodeError:
                        # Stage 5: Resilient Healing for structural inconsistencies
                        try:
                            repaired = clean_line.strip('"').replace('\\"', '"')
                            healed_data = self.sanitize(json.loads(repaired))
                            if self.validate_schema(healed_data):
                                sanitized_compounds.append(healed_data)
                            else:
                                failures += 1
                        except:
                            failures += 1
                            logging.warning(f"Permanent failure at line {line_num}")
                            continue

            logging.info(f"Ingestion Complete: {len(sanitized_compounds)} items loaded. {failures} rejected.")
            return sanitized_compounds

        except FileNotFoundError:
            logging.error(f"Critical Error: File {file_path} not found.")
            return []

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans raw input to prevent injection and processing errors.

        Ensures the NLP model processes pure text rather than markup noise 
        by stripping HTML and unescaping characters.

        Args:
            data (Dict[str, Any]): The raw data dictionary.

        Returns:
            Dict[str, Any]: The sanitized data dictionary.
        """
        # Support both 'raw_text' (SOMA Engine standard) and 'text'
        text_key = "raw_text" if "raw_text" in data else "text"
        text = data.get(text_key, "")
        
        # 1. Strip HTML tags (e.g., <div> -> "")
        clean_text_pattern = re.compile('<.*?>')
        text = re.sub(clean_text_pattern, '', str(text))
        
        # 2. Unescape HTML entities (e.g., &quot; -> ")
        text = html.unescape(text)
        
        # 3. Final trim and key normalization
        data["raw_text"] = text.strip()
        
        return data

    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Verifies that the data structure is complete, correct, and safe.

        Theory - Fail-Fast Principle:
            It is cheaper to stop processing at this gate than to let 
            malformed data consume GPU cycles in the SOMA Engine.

        Args:
            data (Dict[str, Any]): The data to validate.

        Returns:
            bool: True if compliant, False otherwise.
        """
        # Core schema: Must have text and metadata origin
        if not isinstance(data, dict):
            return False

        if "raw_text" not in data or not str(data["raw_text"]).strip():
            logging.error("Validation failed: Missing or empty 'raw_text'.")
            return False
            
        if "metadata" not in data and "origin" not in data:
            logging.error("Validation failed: Missing traceability metadata.")
            return False
        
        return True

# Example Usage for SOMA Batch
if __name__ == "__main__":
    handler = DataHandler()
    target_file = 'soma_registry_batch_20260511_1419.jsonl'
    
    compounds = handler.ingest_registry(target_file)
    print(f"SOMA Registry ready with {len(compounds)} items.")