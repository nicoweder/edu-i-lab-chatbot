import os
import json
import time
import re

# Basisverzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eingabe- und Ausgabeordner relativ zum Projektverzeichnis
INPUT_DIR = os.path.join(BASE_DIR, "data", "clean_articles")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "chunks", "chunks_recursive_overl_30")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_WORDS = 50
MAX_WORDS = 400
OVERLAP_WORDS = 30  

def count_words(text):
    """
    Zählt die Wörter eines Textes.
    """
    return len(text.split())

def split_into_sentences(text):
    """
    Trennt Text in Sätze basierend auf Punkt, Ausrufe- und Fragezeichen.
    """
    return re.split(r'(?<=[.!?])\s+', text)

def recursive_split(text, max_words):
    """
    Zerlegt Text rekursiv in semantisch sinnvolle Chunks.
    Zuerst auf Absatz-, dann Satz-, und schließlich Wortebene.
    """
    if count_words(text) <= max_words:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) > 1:
        chunks = []
        buffer = ""

        for para in paragraphs:
            candidate = f"{buffer}\n\n{para}" if buffer else para
            if count_words(candidate) <= max_words:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(recursive_split(buffer, max_words))
                buffer = para

        if buffer:
            chunks.extend(recursive_split(buffer, max_words))

        return chunks

    sentences = split_into_sentences(text)
    if len(sentences) > 1:
        chunks = []
        buffer = ""

        for s in sentences:
            candidate = f"{buffer} {s}".strip()
            if count_words(candidate) <= max_words:
                buffer = candidate
            else:
                if buffer:
                    chunks.append(buffer)
                buffer = s

        if buffer:
            chunks.append(buffer)

        return chunks

    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def apply_overlap(chunks, overlap_words):
    """
    Fügt den Chunks eine Überlappung von Wörtern hinzu.
    """
    if overlap_words <= 0:
        return chunks

    overlapped = []
    prev_tail = []

    for chunk in chunks:
        words = chunk.split()
        merged = prev_tail + words
        overlapped.append(" ".join(merged))
        prev_tail = words[-overlap_words:] if overlap_words <= len(words) else words

    return overlapped

def chunk_article_recursive(title, url, author, pub_date, content, links, filename):
    """
    Teilt einen Artikel rekursiv in Chunks und speichert diese als JSON-Dateien.
    """
    all_chunks = recursive_split(content, MAX_WORDS)
    all_chunks = apply_overlap(all_chunks, OVERLAP_WORDS)

    for idx, chunk_text in enumerate(all_chunks, start=1):
        chunk_links = [
            link for link in links
            if link.get("anchor") and link["anchor"] in chunk_text
        ]

        chunk_data = {
            "title": title,
            "url": url,
            "author": author,
            "pub_date": pub_date,
            "chunk_index": idx,
            "chunk_text": chunk_text,
            "links": chunk_links
        }

        output_file = f"{os.path.splitext(filename)[0]}_chunk{idx}.json"
        output_path = os.path.join(OUTPUT_DIR, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=4)

        print(f"Chunk {idx} erstellt ({count_words(chunk_text)} Wörter)")
        time.sleep(0.05)

def process_all_articles():
    """
    Verarbeitet alle Artikel im Eingabeverzeichnis und chunked sie rekursiv.
    """
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    for filename in files:
        with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
            article = json.load(f)

        content = article.get("content", "")
        if not content.strip():
            print(f"Überspringe leeren Artikel: {filename}")
            continue

        chunk_article_recursive(
            title=article.get("title", ""),
            url=article.get("url", ""),
            author=article.get("author", ""),
            pub_date=article.get("pub_date", ""),
            content=content,
            links=article.get("links", []),
            filename=filename
        )

        print(f"{filename} verarbeitet\n")

    print("Alle Artikel wurden rekursiv gechunked.")

if __name__ == "__main__":
    process_all_articles()
