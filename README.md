# Edu-I Lab Chatbot – Hochschule Luzern

Dieses Projekt implementiert einen Chatbot für den Edu-I Lab Blog der Hochschule Luzern, der Fragen zu Blogartikeln beantwortet, dabei Quellen angibt und kontextbasiert arbeitet. Der Chatbot nutzt eine Vektordatenbank (FAISS) für semantische Suche und OpenAI GPT-4o für die Antwortgenerierung.

## Projektstruktur

| Datei / Ordner                   | Beschreibung                                                                      |
| -------------------------------- | --------------------------------------------------------------------------------- |
| `preprocessing1.py`              | Liest XML-Export von WordPress ein und speichert Artikel als JSON.                |
| `preprocessing2.py`              | Bereinigt HTML-Inhalte, entfernt Bilder und Tracking-Parameter, extrahiert Links. |
| `chunk_articles_by_paragraph.py` | Chunkt Artikel nach Absätzen für Retrieval.                                       |
| `chunk_articles_by_words.py`     | Chunkt Artikel nach Wortanzahl (fixed size).                                      |
| `chunk_articles_recursive.py`    | Rekursives Chunking mit Überschneidungen zur besseren Kontextabdeckung.           |
| `create_vector_db.py`            | Erstellt FAISS-Vektorindex mit ausgewählten Chunks und Metadaten.                 |
| `search_and_answer.py`           | Kernlogik des Chatbots: RAG-Session, FAISS-Suche, OpenAI-Integration.             |
| `prompts.py`                     | Enthält die finalen Prompt-Varianten für den Chatbot.                             |
| `api.py`                         | Flask-Testumgebung zur Integration als Web-Chatbot.                               |
| `tests/`                         | Testfälle für Evaluation (Fragen, Bewertung).                                     |
| `tests/results/`                 | Ergebnisse von Tests und Evaluationen (JSON, CSV, Plots).                         |


## Installation

1. **Python 3.10+ installieren**

2. Projekt klonen:
```bash
git clone <repository_url>
cd edu-i-lab-chatbot
```
3. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
```
Linux/macOS:
```bash
source venv/bin/activate
```
Windows:
```bash
venv\Scripts\activate
```
4. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```
5. OpenAI API-Key setzen (in .env):

OPENAI_API_KEY=sk-...

## Datenvorbereitung

1. WordPress XML-Export vom live Blog besorgen und  in data/ ablegen. Die Datei hat folgendes Format: (edu-ilab.WordPress.2025-10-07.xml)

2. Preprocessing 1 ausführen – XML zu JSON:
```bash
python preprocessing1.py
```
- Ausgabe: data/articles_json/

3. Preprocessing 2 ausführen – Bereinigung & Link-Extraktion:
```bash
python preprocessing2.py
```
-Ausgabe: data/clean_articles/

## Chunking und Indexierung

Für Retrieval-augmented Generation (RAG) müssen Artikel in Chunks aufgeteilt werden, hierbei soll für die beste Perfomance die in der Dokumentation empfolene konviguration gewählt werden(chunk_articles_by_paragraph.py mit 0 overlap):

- Absatzweise: chunk_articles_by_paragraph.py

- Nach Wortanzahl: chunk_articles_by_words.py

- Rekursiv mit Überschneidungen: chunk_articles_recursive.py

Vektor-Datenbank erstellen(es muss darauf geachtet werden, dass die zuvor erstellten Chunks als Grundlage gewählt werden):
```bash
python create_vector_db.py
```
- Erzeugt FAISS-Index und metadata.pkl für die RAG-Session.

## Terminal-Test

Direkte Nutzung der RAG-Session (zuerst kontrolliern unter EXPERIMENT die vorher erstellten chunks angegeben werden[EXPERIMENT = "chunks_paragraph_no_overlap" ]) dann im Terminal:
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


## Chatbot-API

Falls eine lokale Testumgebung mit Flask aufgesetzt wurde kann hiermit der Chatbot im Frontend getestet werden:
```bash
python api.py
```
- Endpunkt: POST /ask

## Evaluation und Tests

Testfälle: tests/testcases2.json

1. **Experiment auswählen:** In `search_and_answer.py` das gewünschte Experiment auswählen, das den entsprechenden Index in `data/indices/` nutzt. In `evaluation_manual.py` soll derselbe Experiment-Name angegeben werden.  
2. **Backend starten:** Flask-App starten, dazu im Teminal python api.py ausführen.  
3. **Fragen stellen und bewerten:** Skript `evaluation_manual.py` starten, eine Frage in Testumgebung eingeben um Session zu starten. Im Terminal wo api.py ausgeführt wird Session-ID auslesen und im terminal wo evaluation_manual ausgeführt wird eingeben . Fragen im Frontend stellen; das Skript wartet auf die Antwort und fordert im Terminal die manuelle Bewertung für Relevanz, Verständlichkeit, Korrektheit und Quellenqualität an. Die Antwortzeit wird automatisch erfasst.  
4. **Speicherung:** Ergebnisse inkl. Gesamtscore werden fortlaufend in einer JSON-Datei gespeichert unter dem tests Ordner gespeichert. Die Resultate die gespeichert werden wollen in den tests/result ordner verschieben.  
5. **Nächste Frage:** Nach der Bewertung die nächste Frage von testcases2 in Testumgebung eingeben; Skript läuft, bis es manuell mit `STRG+C` beendet wird.

Ergebnisse werden im tests-Ordner abgelegt.

## Visualisierung
- Analysiert Endscore und Metriken über Experimente:
```bash
python results/analyze_results.py
```
- Ausgabe:

- Balkendiagramm experiment_comparison.png

## Prompt-Varianten

FINAL_PROMPT_1 – detailliert, fokussiert auf Kontext und Quellen

FINAL_PROMPT_2 – Chain-of-Thought Ansatz

Wahl innerhalb von search_and_answer.py über final_prompt_variant=1|2.