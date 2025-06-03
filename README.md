# Multi-Format Intake Agent with Intelligent Routing & Context Memory

A Flask-based AI-powered system that accepts multi-format inputs (email, JSON, PDF, plain text), intelligently classifies and routes them to specialized agents for parsing, intent detection, and logging. Supports conversation context memory with SQLite backend.

---

## Features

- **Multi-format input support:** Email, JSON, PDF, and plain text.
- **Intelligent classification:** Uses LangChain + ChatGroq LLM to classify input format and intent.
- **Specialized agents:**  
  - EmailParserAgent: extracts sender, urgency, intent from email content.  
  - JSONAgent: validates and maps JSON input against schema.  
  - PDFAgent: extracts text from PDFs and classifies intent.  
- **Memory Manager:** Logs inputs with metadata, supports conversation-based queries.
- **Flask REST API:** Endpoints for processing different input formats.
- **Simple Bootstrap-based UI:** Paste text or upload JSON/PDF files for testing.
- **Docker-ready:** Easily containerize and deploy.

---

## Getting Started

### Prerequisites

- Python 3.10 (reccommended)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Docker](https://docs.docker.com/get-docker/) (optional, for containerized deployment)
- Groq API Key (for LangChain ChatGroq LLM)

### Setup ( Without Docker )

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/multi-format-intake-agent.git
   cd multi-format-intake-agent

2. Create a `.env` file in the root directory with your Groq API key:  
   Get the keys from [https://console.groq.com/home](https://console.groq.com/home)

   ```ini
   GROQ_API_KEY=your_groq_api_key_here

3. Install all required Python dependencies:

    ```bash
    pip install -r requirements.txt

   
4. Run the Flask app locally:

   ```bash
   python run.py

5. Open your browser at http://127.0.0.1:5000 to access the UI.


### Setup ( With Docker )
   


   
