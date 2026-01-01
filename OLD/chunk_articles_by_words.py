import os
import json

# Basisverzeichnis des Projekts ermitteln
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eingabe- und Ausgabeordner relativ zum Projektverzeichnis
INPUT_DIR = os.path.join(BASE_DIR, "data", "clean_articles")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "chunks", "chunks_words_30")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 300   # Wörter pro Chunk
CHUNK_OVERLAP = 30 # Wörter Überlappung

def chunk_text(text, links, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Teilt den Text in Chunks auf Basis von Wortanzahl auf.
    Jeder Chunk enthält maximal 'size' Wörter und überlappt mit dem vorherigen Chunk um 'overlap' Wörter.
    """
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
            start = end - overlap  # Überlappung berücksichtigen

    return chunks

def process_articles_to_chunks():
    """
    Lädt alle Artikel aus INPUT_DIR, teilt sie in Wort-Chunks und speichert diese in OUTPUT_DIR.
    """
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    total_chunks = 0

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        text = article.get("content", "")
        links = article.get("links", [])
        if not text.strip():
            print(f"Überspringe leeren Artikel: {filename}")
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
        print(f"{filename}: {len(chunks)} Chunks erstellt")

    print(f"Insgesamt {total_chunks} Chunks erstellt.")

if __name__ == "__main__":
    process_articles_to_chunks()
