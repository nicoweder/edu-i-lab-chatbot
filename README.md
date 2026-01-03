# Edu-I Lab Chatbot – Hochschule Luzern

Dieses Projekt implementiert einen Chatbot für den Edu-I Lab Blog der Hochschule Luzern, der Fragen zu Blogartikeln beantwortet, dabei Quellen angibt und kontextbasiert arbeitet. Der Chatbot nutzt eine Vektordatenbank (FAISS) für semantische Suche und OpenAI GPT-4o für die Antwortgenerierung. Die vollständigen Artikel-Chunks und FAISS-Indizes sind aufgrund der Größe nicht im Repository enthalten. Sie müssen durch Ausführen mehrerer Schritte selber erstellt werden.



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
| `OLD/`                             | Enthält ältere Versionen von Skripten und Experimenten                                        |
| `OLD/api_old.py`                   | Alte Version der Flask-Testumgebung                                                         |
| `OLD/chunk_articles_by_words.py`   | Alte Chunking-Variante nach Wortanzahl, wurde für erste Tests verwendet                      |
| `OLD/run_tests_with_eval.py`       | Alte Testskripte für Evaluation                                                              |
| `Frontend/`                         | Enthält die HTML-Datei für den Web-Chatbot                                                  |
| `Frontend/chatbot.html`            | Code für Frontend des Chatbots                                                               |
| `requirements.txt`                 | Listet alle Python-Abhängigkeiten für das Projekt                                             |
| `README.md`                        | Projektbeschreibung, Setup-Anleitung und Nutzungshinweise                                    |
| `.gitignore`                        | Enthält Regeln, welche Dateien/Ordner nicht ins Repository aufgenommen werden sollen         |



## Installation

1. **Python 3.10+ installieren**

2. Projekt klonen:
```bash
git clone <https://github.com/nicoweder/edu-i-lab-chatbot>
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
5. OpenAI API-Key setzen (edu-i-chatbot/.env Datei erstellen und Key angeben):

OPENAI_API_KEY=sk-...


## Datenvorbereitung

1. WordPress XML-Export (die auch abgegeben wurde) vom live Blog besorgen und  in data/ ablegen. Die Datei hat folgendes Format: (edu-ilab.WordPress.2025-10-07.xml)

2. export_to_json ausführen – XML zu JSON:
```bash
python export_to_json.py
```
- Ausgabe: data/articles_json/

3. clean_articles ausführen – Bereinigung & Link-Extraktion:
```bash
python clean_articles.py
```
-Ausgabe: data/clean_articles/

## Chunking und Indexierung

Für Retrieval-augmented Generation (RAG) müssen Artikel in Chunks aufgeteilt werden, hierbei soll für die empfolene Konviguration gewählt werden(chunk_articles_by_paragraph.py mit 0 overlap). Der Name der Chunks ist nach der Konfiguration zu benennen z.B chunks_paragraph_no_overlap:

- Absatzweise: src/chunk_articles_by_paragraph.py

- Nach Wortanzahl: OLD/chunk_articles_by_words.py

- Rekursiv mit Überschneidungen: src/chunk_articles_recursive.py
```bash
python chunk_articles_by_paragraph.py
```
-Ausgabe: data/clean_articles/chunks/Name der angegeben wurde in chunk_articles_by_paragraph.py (chunks_paragraph_no_overlap)

Vektor-Datenbank erstellen, es muss darauf geachtet werden, dass die zuvor erstellten Chunks als Grundlage gewählt werden. Dies geschiet indem man den Namen des erstellten Chunkordners innerhalb von create_vector_db.py angibt (z.B. EXPERIMENT=chunks_paragraph_no_overlap). Danach kann die Vektordatenbank erstellt werden:
```bash
python create_vector_db.py
```
- Erzeugt FAISS-Index und metadata.pkl für die RAG-Session.

## Terminal-Test

Direkte Nutzung der RAG-Session, zuerst kontrolliern unter EXPERIMENT die vorher erstellten chunks angegeben werden(EXPERIMENT = "chunks_paragraph_no_overlap") dann im Terminal:
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
   - Dieser Name **muss mit dem Experimentnamen** im Skript `search_and_answer.py` übereinstimmen, damit die richtigen Indizes und segmentierten JSON-Dokumente geladen werden.

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
python results/analyze_results.py
```
- Ausgabe:

- Balkendiagramm experiment_comparison.png auf dem zu sehen ist, welche Konfiguration die meisten Antworten mit Score >4.5 beantworten konnten.

### Analyse einer Konfiguration
- Analysiert eine Konfiguration auf Durchschnittswerte der Kriterien:
```bash
python results/analyse_best_config.py
```
- Ausgabe:

- Balkendiagramm avg_scores_comparison.png auf dem zu sehen ist, welches Kriterum, welchen durchnittlichen Wert erreicht hat.

## Frontend 

Unter /Frontend/chatbot.html kann der HTML/CSS/JS Code für das Frontend des Chatbots betrachtet werden.

## OLD

Im Ordner "OLD" sind ältere Versionen oder Experimente des vorliegenden Code, die es nicht in die Arbeit geschafft haben abgelegt.