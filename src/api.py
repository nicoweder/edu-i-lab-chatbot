from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

from search_and_answer import RAGChatSession, client, index, metadata

app = Flask(__name__)
CORS(app)

# session_id -> RAGChatSession
sessions = {}

def get_session(session_id=None):
    """
    Liefert die RAGChatSession zu einer Session-ID.
    Wenn keine existiert, wird eine neue erstellt.
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
    data = request.json
    question = data.get("question")
    session_id = data.get("session_id")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    session, actual_session_id = get_session(session_id)
    result = session.ask(question)

    # Nur noch inline_sources zurückgeben
    return jsonify({
        "session_id": actual_session_id,
        "answer": result["answer"],
        "inline_sources": result.get("inline_sources", [])
    })


if __name__ == "__main__":
    app.run(debug=True)