import xml.etree.ElementTree as ET
import json
import os

# ===============================
# Konfiguration
# ===============================
xml_file = "D:\\BAA Code\\data\\edu-ilab.WordPress.2025-10-07.xml"
output_dir = "D:\\BAA Code\\data\\articles_json"       # Ordner, in dem die JSON-Dateien gespeichert werden
os.makedirs(output_dir, exist_ok=True)

# WordPress XML Namespaces
ns = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

# ===============================
# XML parsen
# ===============================
tree = ET.parse(xml_file)
root = tree.getroot()

# ===============================
# Artikel verarbeiten
# ===============================
for item in root.findall('./channel/item'):
    title = item.find('title').text or "No_Title"
    link = item.find('link').text or ""
    content_elem = item.find('content:encoded', ns)
    content = content_elem.text if content_elem is not None else ""
    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
    author_elem = item.find('dc:creator', ns)
    author = author_elem.text if author_elem is not None else ""

    # JSON-Dokument zusammenstellen
    article = {
        "title": title,
        "url": link,
        "author": author,
        "pub_date": pub_date,
        "content": content
    }

    # Dateiname erzeugen (Sonderzeichen entfernen)
    safe_title = "".join(c if c.isalnum() else "_" for c in title)
    file_path = os.path.join(output_dir, f"{safe_title}.json")

    # JSON speichern
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(article, f, ensure_ascii=False, indent=4)

print(f"Fertig! Alle Artikel wurden in '{output_dir}' gespeichert.")