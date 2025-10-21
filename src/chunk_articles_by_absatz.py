import os
import json
import time

# ===============================
# Pfade & Einstellungen
# ===============================
INPUT_DIR = "D:/BAA Code/data/clean_articles"
OUTPUT_DIR = "D:/BAA Code/data/chunks_no_overlap"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_WORDS = 50
MAX_WORDS = 400
OVERLAP_WORDS = 1  # anstelle von Absatz-Überlappung

# ===============================
# Funktion: Artikel in Absatz-Chunks splitten
# ===============================
def chunk_article(title, url, author, pub_date, content, links, filename):
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    total_paragraphs = len(paragraphs)

    # Sonderfall: Artikel nur 1 Absatz oder sehr kurz
    total_words = len(content.split())
    if total_paragraphs == 1 or total_words <= MAX_WORDS:
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
        print(f"📄 Chunk 1 erstellt ({total_words} Wörter, {total_paragraphs} Absätze)")
        time.sleep(1)
        return

    # Normales Chunking für mehrere Absätze
    chunk_index = 1
    i = 0
    prev_chunk_last_words = ""

    while i < total_paragraphs:
        chunk_paragraphs = []
        word_count = 0
        j = i

        while j < total_paragraphs and word_count < MIN_WORDS:
            para_words = len(paragraphs[j].split())
            chunk_paragraphs.append(paragraphs[j])
            word_count += para_words
            j += 1

        chunk_text = "\n\n".join(chunk_paragraphs)

        # 🔁 Überlappung: letzten 50 Wörter vom vorherigen Chunk hinzufügen
        if prev_chunk_last_words:
            chunk_text = prev_chunk_last_words + "\n\n" + chunk_text

        # Update für nächsten Chunk: letzten 50 Wörter speichern
        chunk_words = chunk_text.split()
        if len(chunk_words) > OVERLAP_WORDS:
            prev_chunk_last_words = " ".join(chunk_words[-OVERLAP_WORDS:])
        else:
            prev_chunk_last_words = chunk_text

        # Links auf Chunk beziehen
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

        print(f"📄 Chunk {chunk_index} erstellt ({word_count} Wörter, {len(chunk_paragraphs)} Absätze)")
        chunk_index += 1

        # Nächster Start-Index (kein Absatz-Overlap mehr!)
        i = j
      

# ===============================
# Hauptverarbeitung
# ===============================
def process_all_articles():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        content = article.get("content", "")
        if not content.strip():
            print(f"⚠️  Überspringe leeren Artikel: {filename}")
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

        print(f"✅ {filename} vollständig verarbeitet\n")

    print("\n🎯 Alle Artikel wurden erfolgreich in Chunks aufgeteilt.")

# ===============================
# Einstiegspunkt
# ===============================
if __name__ == "__main__":
    process_all_articles()
