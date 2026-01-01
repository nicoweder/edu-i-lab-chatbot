import sys
import os
import json
import time
import csv

# Pfade für Imports & Testfälle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Aktuelles Verzeichnis (tests)
SRC_DIR = os.path.join(BASE_DIR, "..", "src")          # src-Verzeichnis für Imports
sys.path.append(SRC_DIR)

from search_and_answer import RAGChatSession, client, index, metadata

# Experiment-Metadaten
EXPERIMENT = "chunks_recursive_overl_50"   # Name der Chunking-Strategie
OVERLAP = 50                               # Überlappung in Wörtern
PROMPT_USED = "FINAL_PROMPT_2"             # verwendeter Prompt

# Testfälle laden
TESTFILE = os.path.join(BASE_DIR, "testcases2.json")
with open(TESTFILE, "r", encoding="utf-8") as f:
    testcases = json.load(f)

print(f"{len(testcases)} Testfälle geladen.\n")

# Gewichtung für Endscore
WEIGHTS = {
    "relevance": 0.3,
    "accuracy": 0.25,
    "clarity": 0.15,
    "sources": 0.15,
    "response_time": 0.15
}

def evaluate_manual_input(prompt):
    """
    Fragt den Nutzer nach einem Score von 1 bis 5.
    """
    while True:
        try:
            value = int(input(prompt))
            if 1 <= value <= 5:
                return value
            print("Bitte eine Zahl zwischen 1 und 5 eingeben.")
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl verwenden.")

def compute_endscore(scores, duration):
    """
    Berechnet den Endscore gemäß Gewichtung.
    Antwortzeit wird invertiert gewertet: <3s=5, 2-5s=4, 5-10s=3, >10s=1
    """
    if duration < 3:
        rt_score = 5
    elif duration < 5:
        rt_score = 4
    elif duration < 10:
        rt_score = 3
    else:
        rt_score = 1

    scores["response_time"] = rt_score
    endscore = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    return round(endscore, 2)

# RAG Chat Session initialisieren
session = RAGChatSession(client, index, metadata, top_k=5)
results = []

# Tests ausführen
for idx, testcase in enumerate(testcases):
    frage = testcase["question"]
    print(f"\n({idx+1}/{len(testcases)}) Testfall {testcase['ID']}: {frage}")

    start = time.time()
    try:
        # Chatbot fragen
        res = session.ask(frage)
    except Exception as e:
        # Fehlerhandling: Session zurücksetzen, damit Folgefragen nicht beeinflusst werden
        print(f"Fehler bei der Frage: {e}")
        session.reset()
        res = {"answer": "Fehler beim Abrufen der Antwort.", "inline_sources": []}

    duration = round(time.time() - start, 2)

    # Ausgabe der Antwort
    print("\nAntwort des Chatbots:")
    print(res.get("answer", "Keine Antwort erhalten."))

    # Ausgabe der Quellen
    print("\nQuellen:")
    for s in res.get("inline_sources", []):
        print(f"- {s.get('title', '')} → {s.get('url', '')}")

    # Manuelle Bewertung
    relevance = evaluate_manual_input("Relevance der Antwort (1-5): ")
    clarity = evaluate_manual_input("Verständlichkeit (1-5): ")
    accuracy = evaluate_manual_input("Genauigkeit / Faktentreue (1-5): ")
    sources_score = evaluate_manual_input("Quellenangabe (1-5): ")

    scores = {
        "relevance": relevance,
        "clarity": clarity,
        "accuracy": accuracy,
        "sources": sources_score
    }

    # Endscore berechnen
    endscore = compute_endscore(scores, duration)

    # Ergebnisse speichern
    results.append({
        "ID": testcase["ID"],
        "frage": frage,
        "antwort": res.get("answer", ""),
        "quellen": res.get("inline_sources", []),
        "dauer_s": duration,
        "bewertung": scores,
        "endscore": endscore,
        "experiment": EXPERIMENT,
        "overlap": OVERLAP,
        "prompt": PROMPT_USED
    })

    print(f"→ Dauer: {duration}s | Endscore: {endscore}\n")

# Ergebnisse speichern
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

RESULT_JSON = os.path.join(
    RESULTS_DIR, f"test_results_{EXPERIMENT}_over{OVERLAP}_{PROMPT_USED}.json"
)
RESULT_CSV = os.path.join(
    RESULTS_DIR, f"test_results_{EXPERIMENT}_over{OVERLAP}_{PROMPT_USED}.csv"
)

# Ergebnisse als JSON speichern
with open(RESULT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Ergebnisse als CSV speichern
with open(RESULT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "ID", "Frage", "Antwort", "Quellen", "Antwortzeit (s)",
        "Relevance", "Clarity", "Accuracy", "Sources", "Endscore",
        "Experiment", "Overlap", "Prompt"
    ])
    for r in results:
        src_titles = "; ".join([s.get("title", "") for s in r["quellen"]])
        writer.writerow([
            r["ID"],
            r["frage"],
            r["antwort"],
            src_titles,
            r["dauer_s"],
            r["bewertung"]["relevance"],
            r["bewertung"]["clarity"],
            r["bewertung"]["accuracy"],
            r["bewertung"]["sources"],
            r["endscore"],
            r["experiment"],
            r["overlap"],
            r["prompt"]
        ])

print(f"\nAlle Testfälle bearbeitet. Ergebnisse gespeichert in {RESULT_JSON} und {RESULT_CSV}.")
