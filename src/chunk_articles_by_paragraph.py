import os
import json
import time

# Basisverzeichnis des Projekts ermitteln
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eingabe- und Ausgabeordner relativ zum Projektverzeichnis
INPUT_DIR = os.path.join(BASE_DIR, "data", "clean_articles")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "chunks", "chunks_paragraph_no_overlap")#Name hier angeben
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_WORDS = 50
MAX_WORDS = 400
OVERLAP_WORDS = 0  #Gegebenenfalls anpassen falls mit Overlap gewüscht

def chunk_article(title, url, author, pub_date, content, links, filename):
    """
    Teilt einen Artikel in Chunks basierend auf Absätzen auf.
    Jeder Chunk enthält mindestens MIN_WORDS Wörter und höchstens MAX_WORDS.
    Überlappung von OVERLAP_WORDS wird zwischen den Chunks berücksichtigt.
    """
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    total_paragraphs = len(paragraphs)
    total_words = len(content.split())

    # Sonderfall: Artikel kurz genug für einen einzigen Chunk
    if total_words <= MAX_WORDS:
        chunk_data = {
            "title": title,
            "url": url,
            "author": author,
            "pub_date": pub_date,
            "chunk_index": 1,
            "chunk_text": content,
            "links": links
        }
        output_file = f"{os.path.splitext(filename)[0]}_chunk1.json"
        output_path = os.path.join(OUTPUT_DIR, output_file)
        with open(output_path, "w", encoding="utf-8") as f_out:
            json.dump(chunk_data, f_out, ensure_ascii=False, indent=4)
        print(f"Chunk 1 erstellt ({total_words} Wörter, {total_paragraphs} Absätze)")
        time.sleep(0.1)
        return

    # Normales Chunking
    chunk_index = 1
    i = 0
    prev_chunk_last_words = []

    while i < total_paragraphs:
        chunk_paragraphs = []
        word_count = 0
        j = i

        # Absätze sammeln bis MIN_WORDS erreicht sind
        while j < total_paragraphs and word_count < MIN_WORDS:
            para_words = len(paragraphs[j].split())
            chunk_paragraphs.append(paragraphs[j])
            word_count += para_words
            j += 1

        chunk_text = "\n\n".join(chunk_paragraphs)

        # Überlappung vom vorherigen Chunk vorne hinzufügen
        if prev_chunk_last_words:
            chunk_text = " ".join(prev_chunk_last_words + chunk_text.split())

        # Links, die im Chunk vorkommen
        chunk_links = [link for link in links if link.get("anchor") and link["anchor"] in chunk_text]

        chunk_data = {
            "title": title,
            "url": url,
            "author": author,
            "pub_date": pub_date,
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "links": chunk_links
        }

        output_file = f"{os.path.splitext(filename)[0]}_chunk{chunk_index}.json"
        output_path = os.path.join(OUTPUT_DIR, output_file)
        with open(output_path, "w", encoding="utf-8") as f_out:
            json.dump(chunk_data, f_out, ensure_ascii=False, indent=4)

        print(f"Chunk {chunk_index} erstellt ({len(chunk_text.split())} Wörter, {len(chunk_paragraphs)} Absätze)")

        # Letzte Wörter für Überlappung merken
        prev_chunk_last_words = chunk_text.split()[-OVERLAP_WORDS:] if OVERLAP_WORDS > 0 else []

        chunk_index += 1
        i = j
        time.sleep(0.1)

def process_all_articles():
    """
    Lädt alle Artikel im INPUT_DIR, teilt sie in Chunks und speichert diese im OUTPUT_DIR.
    """
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        content = article.get("content", "")
        if not content.strip():
            print(f"Überspringe leeren Artikel: {filename}")
            continue

        chunk_article(
            title=article.get("title", ""),
            url=article.get("url", ""),
            author=article.get("author", ""),
            pub_date=article.get("pub_date", ""),
            content=content,
            links=article.get("links", []),
            filename=filename
        )

        print(f"{filename} vollständig verarbeitet")

    print("Alle Artikel wurden erfolgreich in Chunks aufgeteilt.")

if __name__ == "__main__":
    process_all_articles()
