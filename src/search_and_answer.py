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
print("📦 Lade FAISS Index und Metadaten...")

index = faiss.read_index(INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

print(f"✅ Index und {len(metadata)} Metadaten-Einträge geladen.\n")

# ===============================
# 🔎 Funktion: Suche ähnliche Chunks
# ===============================
def search_query(query, top_k=5):
    """Sucht die ähnlichsten Chunks für eine Nutzeranfrage."""
    # Embedding für Query erzeugen
    embedding = client.embeddings.create(
        model="text-embedding-3-large",
        input=query
    ).data[0].embedding

    # In numpy-Array konvertieren
    xq = np.array([embedding], dtype=np.float32)

    # Suche im FAISS Index
    distances, indices = index.search(xq, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(distances[0][i])
            results.append(result)

    return results

# ===============================
# 💬 Funktion: Antwort generieren
# ===============================
def answer_query(query, top_k=5):
    """Kombiniert semantische Suche + GPT für eine Antwort."""
    results = search_query(query, top_k=top_k)

    # Kontext zusammenbauen
    context_blocks = []
    for r in results:
        context_blocks.append(f"---\nTitel: {r['title']}\nText: {r['chunk_text']}\n")
    context = "\n".join(context_blocks)

    # Prompt für GPT
    prompt = f"""
    Du bist ein präziser Assistent. Antworte auf die folgende Frage basierend auf dem gegebenen Kontext.
    Wenn die Information nicht im Kontext vorkommt, sage: "Keine Information vorhanden."

    Frage: {query}

    Kontext:
    {context}
    """

    # GPT-4o Anfrage
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer = response.choices[0].message.content.strip()

    # Ergebnisse + Antwort zurückgeben
    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "title": r["title"],
                "url": r.get("url"),
                "score": round(r["score"], 4)
            }
            for r in results
        ]
    }

# ===============================
# 🧠 Beispielnutzung
# ===============================
if __name__ == "__main__":
    query = input("🔍 Frage eingeben: ")
    result = answer_query(query, top_k=5)

    print("\n💬 Antwort:")
    print(result["answer"])
    print("\n📚 Quellen:")
    for s in result["sources"]:
        print(f"- {s['title']} ({s['score']}) → {s['url']}")
