from flask import Flask, request, jsonify, redirect, url_for
from memory.memory import MemoryManager
from agents.json_agent import JSONAgent
from agents.classifier_agent import ClassifierAgent
from dotenv import load_dotenv
import os
from agents.pdf_agent import PDFAgent
import json
app = Flask(__name__)
memory = MemoryManager()

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
classifier = ClassifierAgent(groq_api_key)

json_agent = JSONAgent(memory)

from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/json_extract", methods=["POST"])
def json_extract():
    data = request.json
    raw_json = data.get("json_input")
    conversation_id = data.get("conversation_id", None)

    if not raw_json:
        return jsonify({"error": "No json_input provided"}), 400

    result = json_agent.process(raw_json, conversation_id)

    return jsonify(result)

@app.route("/log", methods=["POST"])
def log_input():
    data = request.json
    memory.log_input(
        source_type=data["source_type"],
        format=data["format"],
        intent=data["intent"],
        content=data["content"],
        conversation_id=data.get("conversation_id")
    )
    return jsonify({"status": "success", "message": "Logged to memory"})

@app.route("/logs/<conversation_id>", methods=["GET"])
def get_by_conversation(conversation_id):
    records = memory.get_by_conversation_id(conversation_id)
    return jsonify(records)

@app.route("/classify", methods=["POST"])
def classify_input():
    data = request.json
    raw_input = data.get("input")
    conversation_id = data.get("conversation_id", None)

    result = classifier.classify(raw_input)
    memory.log_input(
        source_type="auto",
        format=result["format"],
        intent=result["intent"],
        content={"raw": raw_input},
        conversation_id=conversation_id
    )

    return jsonify({"status": "classified", "result": result})

from agents.email_agent import EmailParserAgent

email_agent = EmailParserAgent(memory, classifier)
@app.route("/parse_email", methods=["POST"])
def parse_email():
    data = request.json
    email_content = data.get("email_content")
    conversation_id = data.get("conversation_id")

    if not email_content:
        return jsonify({"error": "email_content is required"}), 400

    result = email_agent.parse_email(email_content, conversation_id)
    return jsonify({"status": "parsed", "result": result})

pdf_agent = PDFAgent(memory, classifier)
@app.route("/parse_pdf", methods=["POST"])
def parse_pdf():
    if "pdf_file" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400
    file = request.files["pdf_file"]
    conversation_id = request.form.get("conversation_id")

    result = pdf_agent.parse_pdf(file, conversation_id)
    return jsonify({"status": "parsed", "result": result})




@app.route("/route_input", methods=["POST"])
def route_input():
    data = request.json
    raw_input = data.get("input")
    conversation_id = data.get("conversation_id", None)

    if not raw_input:
        return jsonify({"error": "Input field is required"}), 400

    # 1. Classify format and intent
    classification = classifier.classify(raw_input)
    input_format = classification.get("format", "unknown")

    # 2. Route based on format
    if input_format == "json":
        try:
            json.loads(raw_input)
            parsed_json_result = json_agent.process(raw_input, conversation_id)

            result = {
                "source": "json_agent",
                "parsed_data": parsed_json_result,
                "classification": classification
            }
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"JSON processing failed: {str(e)}"}), 500

    elif input_format == "email":
        try:
            parsed_email_result = email_agent.parse_email(raw_input, conversation_id)
            result = {
                "source": "email_agent",
                "parsed_data": parsed_email_result,
                "classification": classification
            }
        except Exception as e:
            return jsonify({"error": f"Email processing failed: {str(e)}"}), 500

    else:
        # fallback: just log classification with raw input, no further processing
        memory.log_input(
            source_type="auto",
            format=input_format,
            intent=classification.get("intent", "unknown"),
            content={"raw": raw_input},
            conversation_id=conversation_id
        )
        result = {
            "source": "classifier_only",
            "classification": classification,
            "message": "No specific agent matched the input format."
        }

    # 3. Return merged structured result
    return jsonify({"status": "processed", "result": result})

@app.route("/all_logs")
def all_logs():
    format_filter = request.args.get("format")
    intent_filter = request.args.get("intent")
    conversation_id_filter = request.args.get("conversation_id")

    records = memory.get_filtered_logs(format_filter, intent_filter, conversation_id_filter)

    grouped = {}
    for row in records:
        id, source_type, fmt, intent, content, conv_id, timestamp = row
        entry = {
            "id": id,
            "source_type": source_type,
            "format": fmt,
            "intent": intent,
            "content": json.loads(content),
            "conversation_id": conv_id,
            "timestamp": timestamp
        }
        grouped.setdefault(conv_id or "no_id", []).append(entry)

    return render_template("all_logs.html", grouped_logs=grouped)


@app.route("/delete_log/<int:log_id>", methods=["POST"])
def delete_log(log_id):
    memory.delete_log(log_id)
    return redirect(url_for('all_logs'))

if __name__ == "__main__":
    app.run(debug=True)
