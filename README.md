# Edu-I Lab Chatbot – Hochschule Luzern

Dieses Projekt implementiert einen Chatbot für den Edu-I Lab Blog der Hochschule Luzern, der Fragen zu Blogartikeln beantwortet, dabei Quellen angibt und kontextbasiert arbeitet. Der Chatbot nutzt eine Vektordatenbank (FAISS) für semantische Suche und OpenAI GPT-4o für die Antwortgenerierung. Die vollständigen Artikel-Chunks und FAISS-Indizes sind aufgrund der Größe nicht im Repository enthalten. Sie müssen durch Ausführen mehrerer Schritte (mithilfe der vom Blog stammenden XML-Datei) selber erstellt werden.



## Projektstruktur

| Datei / Ordner                     | Beschreibung                                                                                  |
| --------------------------------- | --------------------------------------------------------------------------------------------- |
| `src/`                             | Enthält alle aktuellen Skripte für Datenaufbereitung, Chunking, Vektorindex und Chatbot-Logik |
| `src/export_to_json.py`            | Liest XML-Export von WordPress ein und speichert Artikel als JSON                              |
| `src/clean_articles.py`            | Bereinigt HTML-Inhalte, entfernt Bilder/Tracking-Parameter und extrahiert Links               |
| `src/chunk_articles_by_paragraph.py` | Chunkt Artikel nach Absätzen für Retrieval auch mit Überschneidungen falls definiert         |
| `src/chunk_articles_recursive.py`  | Rekursives Chunking mit Überschneidungen zur besseren Kontextabdeckung                        |
| `src/create_vector_db.py`          | Erstellt FAISS-Vektorindex mit ausgewählten Chunks und Metadaten                               |
| `src/search_and_answer.py`         | Kernlogik des Chatbots: RAG-Session, FAISS-Suche, OpenAI-Integration                          |
| `src/prompts.py`                   | Enthält die finalen Prompt-Varianten für den Chatbot                                          |
| `src/api.py`                       | Flask-Testumgebung für den Web-Chatbot                                                       |
| `tests/`                           | Testfälle und Analyse-Skripte für Evaluation                                                  |
| `tests/testfälle.py`                | 21 Fragen für Evaluation                                                |
| `tests/results/`                   | Beispieloutputs, Plots und Ergebnisse der Tests                                               |
| `tests/analyse_best_config.py`     | Analysiert die besten Parameterkonfigurationen der Experimente                                |
| `tests/analyse_results.py`         | Visualisiert Test- bzw. Experimentergebnisse                                    |
| `tests/evaluation_manually.py`     | Skript für manuelle Bewertung von Antworten                                                  |
| `Frontend/`                         | Enthält die HTML-Datei für den Web-Chatbot                                                  |
| `Frontend/chatbot.html`            | Code für Frontend des Chatbots                                                               |
| `requirements.txt`                 | Listet alle Python-Abhängigkeiten für das Projekt                                             |
| `README.md`                        | Projektbeschreibung, Setup-Anleitung und Nutzungshinweise                                    |
| `.gitignore`                        | Enthält Regeln, welche Dateien/Ordner nicht ins Repository aufgenommen werden sollen         |



## Installation

1. **Python 3.11.4 oder 3.12 installieren** Achtung: Bei zu neuen Versionen von Python kann es zu Problemen mit requirements kommen.

2. Projekt klonen:
```bash
git clone <https://github.com/nicoweder/edu-i-lab-chatbot>
cd edu-i-lab-chatbot
```
3. Virtuelle Umgebung erstellen:
- Standard:
```bash
python -m venv venv
```
Falls es Probleme mit Python gibt kann auch folgendes gemacht werden:
```bash
py -3.12 -m venv venv
```
Hinweis: "3.12" durch die auf Ihrem Rechner installierte Version ersetzen. Alle Anforderungen funktionieren garantiert mit Python 3.11 oder 3.12.

Mac/Linux Hinweis: Falls python noch auf Python 2 verweist, stattdessen python3 verwenden:
```bash
python3 -m venv venv
```
4. Virtuelle Umgebung starten:
Linux/macOS:
```bash
source venv/bin/activate
```
Windows Powershell:
```bash
venv\Scripts\Activate.ps1
```

Windows CMD:
```bash
venv\Scripts\activate.bat
```
5. Abhängigkeiten installieren:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
6. OpenAI API-Key setzen (edu-i-chatbot/.env Datei erstellen und Key angeben). Dieser wurde aus Sicherheitsgründen nicht angegeben:

OPENAI_API_KEY=sk-...


## Datenvorbereitung

1. WordPress XML-Export vom live Blog besorgen falls man Aktuelle Daten möchte (oder die veraltete abgegebene Datei im data Ordner verwenden) und  in edu-i-chatbot/data ablegen. Die Datei hat folgendes Format: edu-ilab.WordPress.2025-10-07.xml 

2. In richtiges Verzeichniss gehen:
```bash
cd .\src
```

3. export_to_json ausführen – XML zu JSON - Wurde eine neue XML-Datei hochgeladen, muss deren Name im export_to_json angegeben werden.
Ausserdem ist darauf zu achten, dass veraltete Dateien, falls sie existieren zuerst aus data/articles_json/ gelöscht werden sollten.
```bash
python export_to_json.py
```
- Ausgabe: data/articles_json/

4. clean_articles ausführen – Bereinigung & Link-Extraktion :
```bash
python clean_articles.py
```
- Ausgabe: data/clean_articles/

Nun sind alle bereinigten Artikel in einem Strukturierten JSON-Dokument im /data Ordner und bereit für die Segmentierung.
## Chunking und Indexierung

Für Retrieval-augmented Generation (RAG) müssen Artikel in Chunks aufgeteilt werden, hierbei soll für die empfolene Konviguration gewählt werden(chunk_articles_by_paragraph.py mit 0 overlap). Der Name der Chunks ist nach der Konfiguration zu benennen (default: chunks_paragraph_no_overlap). Die kann im jeweiligen Skript ganz oben erfolgen. Es wurden zwei Varianten entwickelt, wobei nur das absatzbasierte Chunking empfohlen wird:

- Absatzweise: src/chunk_articles_by_paragraph.py

- Rekursiv mit Überschneidungen: src/chunk_articles_recursive.py

Möchte man das absatzbasierte chunking verwenden, führe folgendes im edu-i-chatbot/src Verzeichniss aus:
```bash
python chunk_articles_by_paragraph.py
```
- Ausgabe: data/clean_articles/chunks/Name der angegeben wurde in chunk_articles_by_paragraph.py (default: chunks_paragraph_no_overlap)

Alternativ kann auch die Rekursive Strategie versucht werden:
```bash
python chunk_articles_recursive.py
```
- Ausgabe: data/clean_articles/chunks/Name der angegeben wurde in chunk_articles_recursive.py (default: chunks_recursive_no_overlap)

### Vektordatenbank erstellen
Achtung: Dieser Schritt kann nur mit dem angegebenen OPENAI KEY in der edu-i-chatbot/.env Datei ausgeführt werden. 
Beim erstellen der Vektordatenbank, muss darauf geachtet werden, dass die zuvor erstellten Chunks als Grundlage gewählt werden. Dies geschiet indem man den Namen des erstellten Chunkordners innerhalb von create_vector_db.py angibt (default:  EXPERIMENT=chunks_paragraph_no_overlap). Danach kann die Vektordatenbank erstellt werden:
```bash
python create_vector_db.py
```
- Erzeugt FAISS-Index und metadata.pkl für die RAG-Session.

## Terminal-Test
Achtung: Dieser Schritt kann nur mit dem angegebenen OPENAI KEY in der edu-i-chatbot/.env Datei ausgeführt werden. 
Direkte Nutzung der RAG-Session, zuerst kontrollieren ob unter EXPERIMENT die vorher erstellten chunks angegeben werden(EXPERIMENT = "chunks_paragraph_no_overlap") dann im Terminal:
```bash
python search_and_answer.py
```

Beispiel:

Frage: Was ist ein Plagiat?
Antwort: Ein Plagiat ist... [Artikel XYZ]
Quellen:
- Artikel XYZ → https://...


RAGChatSession unterstützt: Kontextbegrenzung, max. Nachrichten, Retry-Mechanismus bei API-Fehlern. Achtung die inline Quellen funktionieren nur im Frontend!

Chat kann zurückgesetzt werden: session.reset()
### Prompt-Varianten

FINAL_PROMPT_1 – detailliert, fokussiert auf Kontext und Quellen

FINAL_PROMPT_2 – Chain-of-Thought Ansatz

Wahl innerhalb von search_and_answer.py über final_prompt_variant=1|2.

## Chatbot-API

Falls eine lokale Testumgebung mit WordPress aufgesetzt wurde kann hiermit der Chatbot im Frontend getestet werden:
```bash
python api.py
```
- Endpunkt: POST /ask

## Manuelle Evaluation der Testfälle

1. **Experiment auswählen**
   - In `evaluation_manually.py` den Namen der zu testenden Konfiguration angeben.
   - Dieser Name **soll mit dem Experimentnamen** im Skript `search_and_answer.py` übereinstimmen, um die Übersicht zu behalten.

2. **Testumgebung starten**
   - Lokale WordPress-Testumgebung starten.

3. **API starten**
   - `api.py` ausführen, um die Verbindung zwischen Frontend (Chatbot) und Backend herzustellen.

4. **Testfälle in den Chatbot eingeben**
   - Erste Frage aus `testfälle.py` oder dem Anforderungskatalog in das Eingabefeld des Chatbots kopieren.
   - Dadurch wird eine neue Chat-Session gestartet.
   - Im Terminal, in dem `api.py` läuft, die **Session-ID** ablesen.

5. **Evaluation starten**
   - Separates Terminal öffnen und `evaluation_manually.py` ausführen.
   - Zu Beginn die zuvor ausgelesene **Session-ID** eingeben.

6. **Kriterien bewerten**
   - Im Terminal erscheint die erste Frage und das erste Bewertungskriterium.
   - Passende Zahl (1–5) eingeben, um das Kriterium zu bewerten.
   - Das Skript fährt automatisch mit dem nächsten Kriterium fort.
   - Antworten im Chatbot prüfen, inkl. Verlinkungen.

7. **Weitere Testfälle**
   - Vorgang wiederholen: Frage in Chatbot kopieren → Kriterien bewerten → nächster Testfall.

8. **Ergebnisse speichern**
   - Die Bewertung wird automatisch in einer **JSON-Datei** unter `tests/` abgelegt.
   - Nach Abschluss können die Dateien nach `tests/results/` verschoben werden, um eine strukturierte Übersicht zu erhalten.


## Visualisierung
- Analysiert Endscore über Experimente:
```bash
python tests/analyze_results.py
```
- Ausgabe:

- Balkendiagramm experiment_comparison.png auf dem zu sehen ist, welche Konfiguration die meisten Antworten mit Score >4.5 beantworten konnten.

### Analyse einer Konfiguration
- Analysiert eine Konfiguration auf Durchschnittswerte der Kriterien:
```bash
python tests/analyse_best_config.py
```
- Ausgabe:

- Balkendiagramm avg_scores_comparison.png auf dem zu sehen ist, welches Kriterum, welchen durchnittlichen Wert erreicht hat.

## Frontend 

Unter edu-i-chatbot/Frontend/chatbot.html kann der HTML/CSS/JS Code für das Frontend des Chatbots betrachtet werden.

