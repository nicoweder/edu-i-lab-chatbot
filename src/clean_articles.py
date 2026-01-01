import os
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup

# Basisverzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eingabe- und Ausgabeordner relativ zum Projektverzeichnis
INPUT_DIR = os.path.join(BASE_DIR, "data", "articles_json")    # Originalartikel
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "clean_articles")  # Bereinigte Artikel
os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_url(url):
    """
    Entfernt Tracking-Parameter (utm_*) und trailing slashes aus URLs.
    """
    try:
        p = urlparse(url)
        qs = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith("utm_")]
        new_q = urlencode(qs)
        cleaned = urlunparse((p.scheme, p.netloc, p.path, p.params, new_q, p.fragment))
        return cleaned.rstrip("/")
    except Exception:
        return url

def clean_html_and_extract_links(html):
    """
    Entfernt HTML, wandelt <p> und <br> in Absatztrennungen um und extrahiert Links.
    """
    if not html or not isinstance(html, str):
        return "", []

    soup = BeautifulSoup(html, "html.parser")

    # <img>-Tags entfernen
    for img in soup.find_all("img"):
        img.decompose()

    # Links extrahieren
    links = []
    for a in soup.find_all("a", href=True):
        href = normalize_url(a["href"].strip())
        anchor = a.get_text(strip=True)
        if href:
            links.append({
                "href": href,
                "anchor": anchor or None
            })

    # <br> → \n\n
    for br in soup.find_all("br"):
        br.replace_with("\n\n")

    # <p> → \n\n
    for p in soup.find_all("p"):
        p.insert_before("\n\n")

    # Gesamten Text extrahieren
    clean_text = soup.get_text(separator=" ", strip=True)
    clean_text = clean_text.replace("\n \n", "\n\n").strip()

    return clean_text, links

def process_articles():
    """
    Verarbeitet alle Artikel im Eingabeverzeichnis:
    - HTML bereinigen
    - Links extrahieren
    - Sehr kurze Artikel überspringen
    - Bereinigte Artikel als JSON speichern
    """
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"Starte Bereinigung von {len(files)} Artikeln...\n")

    skipped = 0
    saved = 0

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        content = article.get("content", "")
        if not content or not isinstance(content, str):
            print(f"Überspringe leeren Artikel: {filename}")
            skipped += 1
            continue

        clean_text, links = clean_html_and_extract_links(content)

        word_count = len(clean_text.split())
        if word_count < 30:
            print(f"Überspringe zu kurzen Artikel ({word_count} Wörter): {filename}")
            skipped += 1
            continue

        cleaned_article = {
            "title": article.get("title", ""),
            "url": normalize_url(article.get("url", "")),
            "author": article.get("author", ""),
            "pub_date": article.get("pub_date", ""),
            "content": clean_text,
            "links": links
        }

        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_article, f, ensure_ascii=False, indent=4)

        saved += 1
        print(f"Gespeichert: {filename} ({word_count} Wörter)")

    print(f"\nFertig! {saved} Artikel bereinigt und gespeichert.")
    print(f"{skipped} Artikel wurden übersprungen (leer oder <30 Wörter).")

if __name__ == "__main__":
    process_articles()
