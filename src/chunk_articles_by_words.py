import os
import json

# ===============================
# Pfade & Einstellungen
# ===============================
INPUT_DIR = "D:/BAA Code/data/clean_articles" # Bereinigte Artikel
OUTPUT_DIR = "D:/BAA Code/data/chunks"        # Speicherort für Chunks
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 300   # Wörter pro Chunk
CHUNK_OVERLAP = 30 # Wörter Überlappung

# ===============================
# Text in Wort-Chunks aufteilen
# ===============================
def chunk_text(text, links, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    chunk_index = 1

    for para in paragraphs:
        words = para.split()
        start = 0
        while start < len(words):
            end = start + size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            # Nur Links behalten, deren Anchor im Chunk vorkommt
            chunk_links = [link for link in links if link.get("anchor") and link["anchor"] in chunk_text]
            chunks.append({
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "links": chunk_links
            })
            chunk_index += 1
            start = end - overlap  # Überlappung

    return chunks

# ===============================
# Hauptverarbeitung
# ===============================
def process_articles_to_chunks():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    total_chunks = 0

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        text = article.get("content", "")
        links = article.get("links", [])
        if not text.strip():
            print(f"⚠️  Überspringe leeren Artikel: {filename}")
            continue

        chunks = chunk_text(text, links, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk in chunks:
            chunk_data = {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "author": article.get("author", ""),
                "pub_date": article.get("pub_date", ""),
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "links": chunk["links"]
            }
            output_file = f"{os.path.splitext(filename)[0]}_chunk{chunk['chunk_index']}.json"
            output_path = os.path.join(OUTPUT_DIR, output_file)
            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(chunk_data, f_out, ensure_ascii=False, indent=4)

        total_chunks += len(chunks)
        print(f"✅ {filename}: {len(chunks)} Chunks erstellt")

    print(f"\n🎯 Fertig! Insgesamt {total_chunks} Chunks erstellt.")

# ===============================
# Einstiegspunkt
# ===============================
if __name__ == "__main__":
    process_articles_to_chunks()
