import os
import json
import faiss
import numpy as np
import pickle
from openai import OpenAI
from dotenv import load_dotenv

# ===============================
# Environment und Pfade
# ===============================
load_dotenv()

# Basisverzeichnis relativ zum aktuellen Skript
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Experiment auswählen (kann für andere Chunking-Strategien geändert werden)
EXPERIMENT = "chunks_paragraph_100"

# Verzeichnisse für Chunks und Index
CHUNKS_DIR = os.path.join(BASE_DIR, "data", "chunks", EXPERIMENT)
INDEX_DIR = os.path.join(BASE_DIR, "data", "indices", EXPERIMENT)
os.makedirs(INDEX_DIR, exist_ok=True)

# Pfade für FAISS-Index und Metadaten
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.pkl")

# API-Key aus .env laden
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY nicht gesetzt (.env fehlt?)")

# OpenAI Client initialisieren
client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# Funktion zur Erstellung von Embeddings
# ===============================
def get_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# ===============================
# Chunks laden und Embeddings erzeugen
# ===============================
chunk_files = sorted([f for f in os.listdir(CHUNKS_DIR) if f.endswith(".json")])

embeddings = []
metadata = []

for filename in chunk_files:
    path = os.path.join(CHUNKS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        chunk = json.load(f)

    embedding = get_embedding(chunk["chunk_text"])
    embeddings.append(embedding)

    metadata.append({
        "title": chunk["title"],
        "url": chunk["url"],
        "chunk_index": chunk["chunk_index"],
        "chunk_text": chunk["chunk_text"],
        "links": chunk.get("links", [])
    })

print(f"Verarbeitet: {len(embeddings)} Chunks")

# ===============================
# FAISS-Index erstellen
# ===============================
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.stack(embeddings))

# Index speichern
faiss.write_index(index, FAISS_INDEX_PATH)
print(f"FAISS Index gespeichert unter: {FAISS_INDEX_PATH}")

# ===============================
# Metadaten speichern
# ===============================
with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"Metadaten gespeichert unter: {METADATA_PATH}")
