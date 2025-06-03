import re
from bs4 import BeautifulSoup
from agents.classifier_agent import ClassifierAgent
from rapidfuzz import fuzz
import json

class EmailParserAgent:
    def __init__(self, memory_manager, classifier_agent):
        self.memory = memory_manager
        self.classifier = classifier_agent

    def extract_urgency(self, email_text):
        urgent_keywords = ['urgent', 'asap', 'immediately', 'high priority', 'important', 'soon']
        temporal_keywords = ['today', 'tomorrow', 'by tomorrow', 'next day', 'imminent', 'urgent delivery']

        email_lower = email_text.lower()

        # Combine all keywords
        keywords = urgent_keywords + temporal_keywords

        # Check fuzzy match with threshold
        threshold = 80  # 0 to 100 scale, tweak as needed

        for kw in keywords:

            if fuzz.partial_ratio(kw, email_lower) >= threshold:
                return "high"

        return "normal"

    def extract_sender(self, email_input):
        # Check if input is JSON string or dict
        if isinstance(email_input, dict):
            # Direct JSON dict input
            sender = email_input.get("sender")
            if sender:
                return sender
        else:
            # Try to parse as JSON string
            try:
                data = json.loads(email_input)
                sender = data.get("sender")
                if sender:
                    return sender
            except (json.JSONDecodeError, TypeError):
                pass

            # Fallback to regex from raw email text
            match = re.search(r"From:\s*(.*)", email_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "unknown"

    def parse_email(self, email_input, conversation_id=None):
        # If input is JSON, get body or text content for urgency/classifier
        if isinstance(email_input, dict):
            text_content = email_input.get("body", "")
        else:
            # If raw email text (string), extract text from HTML or plain
            if bool(BeautifulSoup(email_input, "html.parser").find()):
                soup = BeautifulSoup(email_input, "html.parser")
                text_content = soup.get_text(separator=" ", strip=True)
            else:
                text_content = email_input

        sender = self.extract_sender(email_input)
        urgency = self.extract_urgency(text_content)
        intent_result = self.classifier.classify(text_content)

        self.memory.log_input(
            source_type="email",
            format="email",
            intent=intent_result.get("intent", "unknown"),
            content={
                "sender": sender,
                "urgency": urgency,
                "raw_text": text_content,
                "intent_details": intent_result
            },
            conversation_id=conversation_id
        )

        return {
            "sender": sender,
            "urgency": urgency,
            "intent": intent_result.get("intent", "unknown")
        }
