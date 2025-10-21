import os
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from bs4 import BeautifulSoup

# ===============================
# Pfade
# ===============================
INPUT_DIR = "D:/BAA Code/data/articles_json"   # Originalartikel
OUTPUT_DIR = "D:/BAA Code/data/clean_articles" # Bereinigte Artikel
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===============================
# URL Normalisierung
# ===============================
def normalize_url(url):
    """Entfernt Tracking-Parameter (utm_*) und trailing slashes aus URLs"""
    try:
        p = urlparse(url)
        qs = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith("utm_")]
        new_q = urlencode(qs)
        cleaned = urlunparse((p.scheme, p.netloc, p.path, p.params, new_q, p.fragment))
        return cleaned.rstrip("/")  # Schöner, konsistenter Look
    except Exception:
        return url

# ===============================
# HTML Bereinigung & Linkextraktion
# ===============================
def clean_html_and_extract_links(html):
    """Entfernt HTML, extrahiert reinen Text und Links mit Ankertext."""
    if not html or not isinstance(html, str):
        return "", []

    soup = BeautifulSoup(html, "html.parser")

    # Alle <img>-Tags entfernen (nicht nötig für Textanalyse)
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

    # Nur sichtbaren Text extrahieren
    clean_text = soup.get_text(separator=" ", strip=True)

    return clean_text, links

# ===============================
# Hauptverarbeitung
# ===============================
def process_articles():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"🔍 Starte Bereinigung von {len(files)} Artikeln...\n")

    skipped = 0
    saved = 0

    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            article = json.load(f)

        content = article.get("content", "")
        if not content or not isinstance(content, str):
            print(f"⚠️  Überspringe leeren Artikel: {filename}")
            skipped += 1
            continue

        # Text & Links extrahieren
        clean_text, links = clean_html_and_extract_links(content)

        # Sehr kurze Artikel überspringen
        

        # Neues JSON mit bereinigtem Inhalt & Metadaten
        cleaned_article = {
            "title": article.get("title", ""),
            "url": normalize_url(article.get("url", "")),
            "author": article.get("author", ""),
            "pub_date": article.get("pub_date", ""),
            "content": clean_text,
            "links": links  # Liste mit {href, anchor}
        }

        # Neue Datei speichern
        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_article, f, ensure_ascii=False, indent=4)

        saved += 1
        print(f"✅ Gespeichert: {filename}")

    print(f"\n✅ Fertig! {saved} Artikel bereinigt und gespeichert.")
    print(f"🗑️  {skipped} Artikel wurden übersprungen (leer oder zu kurz).")

# ===============================
# Einstiegspunkt
# ===============================
if __name__ == "__main__":
    process_articles()