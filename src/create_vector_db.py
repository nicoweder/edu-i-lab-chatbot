import os
import json
import faiss
import numpy as np
import pickle
from openai import OpenAI
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Ermittlung des Basisverzeichnisses relativ zum aktuellen Skript
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Auswahl der verwendeten Chunking-Strategie
EXPERIMENT = "chunks_paragraph_no_overlap"

# Definition der Verzeichnisse für Text-Chunks und den zugehörigen FAISS-Index
CHUNKS_DIR = os.path.join(BASE_DIR, "data", "chunks", EXPERIMENT)
INDEX_DIR = os.path.join(BASE_DIR, "data", "indices", EXPERIMENT)
os.makedirs(INDEX_DIR, exist_ok=True)

# Festlegung der Speicherpfade für den FAISS-Index und die Metadaten
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.pkl")

# Laden des OpenAI API-Schlüssels aus den Umgebungsvariablen
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY nicht gesetzt (.env fehlt?)")

# Initialisierung des OpenAI-Clients
client = OpenAI(api_key=OPENAI_API_KEY)

# Erzeugt ein Vektor-Embedding für den gegebenen Text mithilfe des definierten Modells
def get_embedding(text, model="text-embedding-3-large"):
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# Laden aller Chunk-Dateien und sukzessive Erzeugung der zugehörigen Embeddings
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

# Erstellung eines FAISS-Index auf Basis der generierten Embeddings
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.stack(embeddings))

# Persistente Speicherung des FAISS-Index auf dem Dateisystem
faiss.write_index(index, FAISS_INDEX_PATH)
print(f"FAISS Index gespeichert unter: {FAISS_INDEX_PATH}")

# Speicherung der zugehörigen Metadaten zur späteren Rekonstruktion der Inhalte
with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"Metadaten gespeichert unter: {METADATA_PATH}")
