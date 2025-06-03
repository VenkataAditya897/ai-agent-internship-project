import json
from memory.memory import MemoryManager
from datetime import datetime

class JSONAgent:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        # Define required schema keys
        self.required_fields = ["id", "timestamp", "type", "details"]

    def validate_and_map(self, input_json: dict):
        # Check for missing or empty values, not just missing keys
        missing_fields = [field for field in self.required_fields if not input_json.get(field)]

        # Validate timestamp if present
        timestamp_valid = True
        if input_json.get("timestamp"):
            try:
                datetime.fromisoformat(input_json["timestamp"])
            except Exception:
                timestamp_valid = False

        validation_result = {
            "missing_fields": missing_fields,
            "timestamp_valid": timestamp_valid,
            "is_valid": (len(missing_fields) == 0 and timestamp_valid)
        }

        mapped_data = {key: input_json.get(key) for key in self.required_fields}

        return mapped_data, validation_result


    def preprocess_input(self, input_json):
        # Infer type (intent)
        if input_json.get("invoice_number") or input_json.get("invoice_date") or input_json.get("date"):
            inferred_type = "invoice"
        elif input_json.get("request_details"):
            inferred_type = "RFQ"
        else:
            inferred_type = None

        return {
            # "id": input_json.get("invoice_number") or "unknown",
            "id": input_json.get("invoice_number") or input_json.get("id") or "unknown",

            "timestamp": input_json.get("invoice_date") or input_json.get("date"),
            "type": inferred_type,
            "details": {
                "sender": input_json.get("sender"),
                "subject": input_json.get("subject"),
                "request": input_json.get("request_details"),
                "urgency": input_json.get("urgency"),
                "customer": input_json.get("customer"),
                "items": input_json.get("items"),
                "total": input_json.get("total")
            }
        }

    def process(self, raw_json_str, conversation_id=None):
        try:
            input_json = json.loads(raw_json_str) if isinstance(raw_json_str, str) else raw_json_str
        except Exception as e:
            return {"error": f"Invalid JSON: {str(e)}"}

        preprocessed = self.preprocess_input(input_json)
        mapped_data, validation_result = self.validate_and_map(preprocessed)

        self.memory.log_input(
            source_type="json",
            format="json",
            intent=input_json.get("intent", "unknown"),
            content=mapped_data,
            conversation_id=conversation_id
        )

        return {
            "mapped_data": mapped_data,
            "validation": validation_result
        }
