import os
import json
import faiss
import numpy as np
from openai import OpenAI

# ===============================
# Pfade & Einstellungen
# ===============================
CHUNKS_DIR = "D:/BAA Code/data/chunks_overlap50w"
FAISS_INDEX_PATH = "D:/BAA Code/data/faiss_index.index"
OPENAI_API_KEY = "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"  # Setze hier deinen API Key

# OpenAI Client initialisieren
client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# Funktion: Embeddings erzeugen
# ===============================
def get_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# ===============================
# Chunks laden und Embeddings erstellen
# ===============================
chunk_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith(".json")]

embeddings_list = []
metadata_list = []

for filename in chunk_files:
    file_path = os.path.join(CHUNKS_DIR, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        chunk = json.load(f)

    text = chunk["chunk_text"]
    emb = get_embedding(text)
    embeddings_list.append(emb)

    # Metadata speichern für spätere Zuordnung
    metadata_list.append({
    "title": chunk["title"],
    "url": chunk["url"],
    "chunk_index": chunk["chunk_index"],
    "chunk_text": chunk["chunk_text"],
    "links": chunk.get("links", [])
})

print(f"✅ Embeddings für {len(embeddings_list)} Chunks erstellt")

# ===============================
# FAISS Index erstellen
# ===============================
dimension = len(embeddings_list[0])
index = faiss.IndexFlatL2(dimension)  # L2 Distance
index.add(np.stack(embeddings_list))

# Index speichern
faiss.write_index(index, FAISS_INDEX_PATH)
print(f"✅ FAISS Index gespeichert unter {FAISS_INDEX_PATH}")

# ===============================
# Optional: Metadata parallel speichern
# ===============================
import pickle
with open("D:/BAA Code/data/faiss_metadata.pkl", "wb") as f:
    pickle.dump(metadata_list, f)

print("✅ Metadata gespeichert")
