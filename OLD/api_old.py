from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

from search_and_answer import RAGChatSession, client, index, metadata

# Flask-App initialisieren
app = Flask(__name__)
CORS(app)

# Dictionary zum Speichern der Chat-Sessions: session_id -> RAGChatSession
sessions = {}

def get_session(session_id=None):
    """
    Liefert die RAGChatSession zu einer gegebenen Session-ID zurück.
    Falls keine Session-ID existiert oder ungültig ist, wird eine neue Session erzeugt.
    """
    if session_id and session_id in sessions:
        return sessions[session_id], session_id

    new_id = session_id or str(uuid.uuid4())
    sessions[new_id] = RAGChatSession(
        client=client,
        index=index,
        metadata=metadata
    )
    return sessions[new_id], new_id

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpunkt zum Stellen von Fragen an den Chatbot.
    Erwartet JSON mit 'question' und optional 'session_id'.
    Gibt JSON zurück mit 'session_id', 'answer' und 'inline_sources'.
    """
    data = request.json
    question = data.get("question")
    session_id = data.get("session_id")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    session, actual_session_id = get_session(session_id)
    result = session.ask(question)

    return jsonify({
        "session_id": actual_session_id,
        "answer": result["answer"],
        "inline_sources": result.get("inline_sources", [])
    })

if __name__ == "__main__":
    # App lokal starten (Debug=True nur für Entwicklung)
    app.run(debug=True)
