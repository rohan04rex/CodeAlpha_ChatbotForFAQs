"""
CodeAlpha AI Internship - Task 2: Chatbot for FAQs
Flask Web Application Server
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from chatbot_engine import FAQChatbotEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Flask 3 uses the JSON provider instead of the removed JSON_AS_ASCII config key.
app.json.ensure_ascii = False

# Initialize the NLP Chatbot Engine
engine = FAQChatbotEngine()

@app.route("/")
def index():
    """Renders the interactive Chatbot web interface."""
    categories = engine.get_categories()
    faqs = engine.get_all_faqs()
    return render_template("index.html", categories=categories, faqs=faqs)

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main Chat API Endpoint.
    Receives user message and returns best-matching answer via NLP Cosine Similarity.
    """
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message cannot be empty."
            }), 400

        history = data.get("history", [])
        result = engine.find_best_match(message, history=history)
        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        logger.error(f"Chat API error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An error occurred while processing your message."
        }), 500

@app.route("/api/faqs", methods=["GET"])
def get_faqs():
    """Returns all FAQ questions and categories."""
    category = request.args.get("category")
    all_faqs = engine.get_all_faqs()
    if category:
        filtered = [f for f in all_faqs if f.get("category") == category]
        return jsonify({"status": "success", "faqs": filtered})
    return jsonify({"status": "success", "faqs": all_faqs})

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns list of FAQ categories."""
    return jsonify({
        "status": "success",
        "categories": engine.get_categories()
    })


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check used by the PRD and deployment platforms."""
    return jsonify({"status": "success", "message": "Chatbot service is running."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "127.0.0.1")
    # The Werkzeug debugger is disabled by default; enable only in development.
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    print(f"Starting CodeAlpha FAQ Chatbot at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
