import xml.etree.ElementTree as ET
import json
import os

# Basisverzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pfade zum XML-Export und Ausgabeordner (relativ zum Projektverzeichnis)
XML_FILE = os.path.join(BASE_DIR, "data", "edu-ilab.WordPress.2025-10-07.xml")# Name hier anpassen falls neue .xml Datei
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "articles_json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# WordPress XML Namespaces
NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

# XML-Datei parsen
tree = ET.parse(XML_FILE)
root = tree.getroot()

# Alle Artikel auslesen und als JSON speichern
for item in root.findall('./channel/item'):
    title = item.find('title').text or "No_Title"
    link = item.find('link').text or ""
    content_elem = item.find('content:encoded', NS)
    content = content_elem.text if content_elem is not None else ""
    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
    author_elem = item.find('dc:creator', NS)
    author = author_elem.text if author_elem is not None else ""

    # JSON-Dokument erstellen
    article = {
        "title": title,
        "url": link,
        "author": author,
        "pub_date": pub_date,
        "content": content
    }

    # Dateiname erzeugen, Sonderzeichen ersetzen
    safe_title = "".join(c if c.isalnum() else "_" for c in title)
    file_path = os.path.join(OUTPUT_DIR, f"{safe_title}.json")

    # JSON speichern
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=4)

print(f"Fertig! Alle Artikel wurden in '{OUTPUT_DIR}' gespeichert.")
