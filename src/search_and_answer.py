import os
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv  
import pickle

# ===============================
# 🔐 .env Datei laden
# ===============================
load_dotenv()  # lädt deinen OPENAI_API_KEY aus .env

# ===============================
# 🧩 Einstellungen
# ===============================
BASE_DIR = "D:/BAA Code/data"
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")

METADATA_PATH = os.path.join(BASE_DIR, "faiss_metadata.pkl")

# OpenAI-Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================
# 🔍 FAISS Index & Metadaten laden
# ===============================
print("Lade FAISS Index und Metadaten...")

index = faiss.read_index(INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

print(f"Index und {len(metadata)} Metadaten-Einträge geladen.\n")

class RAGChatSession:
    def __init__(self, client, index, metadata, top_k=5):
        self.client = client
        self.index = index
        self.metadata = metadata
        self.top_k = top_k
        self.history = []  # speichert Chatverlauf

    def search(self, query):
        embedding = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        ).data[0].embedding

        xq = np.array([embedding], dtype=np.float32)
        distances, indices = self.index.search(xq, self.top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                m = self.metadata[idx].copy()
                m["score"] = float(distances[0][i])
                results.append(m)
        return results

    def build_context(self, results):
        blocks = []
        for r in results:
            blocks.append(
                f"---\nTitel: {r['title']}\nText: {r['chunk_text']}\n"
            )
        return "\n".join(blocks)

    def ask(self, query):
        results = self.search(query)
        context = self.build_context(results)

        # Chatverlauf in den Prompt integrieren
        history_text = ""
        for item in self.history:
            history_text += f"User: {item['user']}\nAssistant: {item['assistant']}\n\n"

        prompt = f"""
Du bist ein faktenbasierter Chatbot für den Edu-I Lab Blog der Hochschule Luzern.
Nutze den Chatverlauf unten, aber beantworte JEDE Frage nur basierend auf dem Kontext.

Chatverlauf:
{history_text}

Regeln:
1. Wenn die Antwort nicht eindeutig aus dem Kontext ableitbar ist, schreibe:
"Keine Information im vorhandenen Kontext."
2. Verwende pro relevanter Aussage eine Inline-Quelle im Format:
[Titel_des_Artikels]
3. Keine Erfindungen, keine Vermutungen.
4. Schreib kurz und präzise.

Aktuelle Frage:
{query}

Kontext:
{context}

Gib NUR die Antwort mit Inline-Quellen.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        answer = response.choices[0].message.content.strip()

        # Verlauf speichern
        self.history.append({
            "user": query,
            "assistant": answer
        })

        return {
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "title": r["title"],
                    "url": r.get("url"),
                    "score": round(r["score"], 4)
                } for r in results
            ]
        }

# ===============================
# 🧠 Beispielnutzung
# ===============================
if __name__ == "__main__":
    session = RAGChatSession(client, index, metadata)

    while True:
        query = input("\nFrage: ")
        if query.lower() in ["exit", "quit", "stop"]:
            break

        result = session.ask(query)

        print("\nAntwort:")
        print(result["answer"])
        print("\nQuellen:")
        for s in result["sources"]:
            print(f"- {s['title']} ({s['score']}) → {s['url']}")