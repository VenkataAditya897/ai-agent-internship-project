import fitz  # PyMuPDF
 # Assuming you have this
from datetime import datetime
import re

class PDFAgent:
    def __init__(self, memory, classifier):
        self.memory = memory
        self.classifier = classifier
    def clean_excerpt(self, text):
        # Collapse multiple newlines, trim extra spaces, and join into paragraphs
        cleaned = re.sub(r'\n+', '\n', text.strip())         # Remove excessive newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)            # Normalize whitespace
        cleaned = cleaned.replace('\n', ' ')                 # replace newlines with space
        cleaned = re.sub(r"Page \d+ of \d+", "", cleaned, flags=re.IGNORECASE)

        return cleaned
    def parse_pdf(self, file_storage, conversation_id=None):
        # Read text from PDF
        doc = fitz.open(stream=file_storage.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        doc.close()

        # Classify content
        result = self.classifier.classify(text)
        format_detected = "pdf"
        intent = result["intent"]

        # Store in memory
        self.memory.log_input(
            source_type="pdf",
            format=format_detected,
            intent=intent,
            content={"text": text},
            conversation_id=conversation_id
        )
        excerpt = self.clean_excerpt(text[:500])
        return {
            "text_excerpt": excerpt,
            "intent": intent,
            "format": format_detected,
            "timestamp": str(datetime.now())
        }
