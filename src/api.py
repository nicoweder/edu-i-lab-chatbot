from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time
import logging

from search_and_answer import RAGChatSession, client, index, metadata


# Initialisierung der Flask-Applikation
app = Flask(__name__)
CORS(app)

# Speicherung aktiver Sessions (session_id → RAGChatSession)
sessions = {}

# Speicherung der letzten Antwort pro Session für Evaluationszwecke
latest_results = {}


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

    #  Debug-Ausgabe
    logging.info(f"Neue Chat-Session erstellt: {new_id}")

    return sessions[new_id], new_id


@app.route("/ask", methods=["POST"])
def ask():
    """
    Zentrale API-Schnittstelle für Nutzeranfragen.

    Erwartet ein JSON-Objekt mit:
    - question: Nutzerfrage
    - session_id (optional): bestehende Session

    Gibt die generierte Antwort, verwendete Quellen und die Antwortzeit zurück.
    """
    data = request.json
    question = data.get("question")
    session_id = data.get("session_id")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    session, actual_session_id = get_session(session_id)

    start_time = time.time()
    result = session.ask(question)
    duration = round(time.time() - start_time, 2)

    # Speicherung der letzten Antwort zur späteren Evaluation
    latest_results[actual_session_id] = {
        "question": question,
        "answer": result.get("answer"),
        "inline_sources": result.get("inline_sources", []),
        "response_time": duration
    }

    return jsonify({
        "session_id": actual_session_id,
        "answer": result.get("answer"),
        "inline_sources": result.get("inline_sources", []),
        "response_time": duration
    })


@app.route("/last_result/<session_id>", methods=["GET"])
def last_result(session_id):
    """
    Gibt das zuletzt gespeicherte Ergebnis einer Session zurück.
    Dieser Endpunkt wird für die manuelle Evaluation verwendet.
    """
    if session_id not in latest_results:
        return jsonify({"error": "No result for this session"}), 404

    return jsonify(latest_results[session_id])


if __name__ == "__main__":
    app.run(debug=True)
