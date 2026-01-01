import requests
import time
import json
import os

# -----------------------
# Experiment-Metadaten
# -----------------------
EXPERIMENT = "chunks_recursive_no_over"
OVERLAP = 0
PROMPT_USED = "FINAL_PROMPT_2"

# Session-ID der laufenden Chat-Session abfragen
SESSION_ID = input("Session-ID eingeben: ")

BASE_URL = "http://127.0.0.1:5000"
print("Warte auf Antworten aus dem Frontend...")
print("Beende das Skript manuell mit STRG+C, wenn alle Tests abgeschlossen sind.\n")

# Ergebnisliste initialisieren
results = []

# JSON-Datei mit Experiment-Metadaten im Namen
json_filename = f"evaluation_results_{EXPERIMENT}_over{OVERLAP}_{PROMPT_USED}.json"
if os.path.exists(json_filename):
    with open(json_filename, "r", encoding="utf-8") as f:
        results = json.load(f)

def rate(name):
    """Fragt den Benutzer nach einer Bewertung zwischen 1 und 5."""
    while True:
        try:
            v = int(input(f"{name} (1–5): "))
            if 1 <= v <= 5:
                return v
        except ValueError:
            pass

def is_already_evaluated(question_text):
    """Prüft, ob diese Frage bereits bewertet wurde."""
    return any(r["question"] == question_text for r in results)

try:
    while True:
        # Warten, bis eine neue Antwort verfügbar ist
        while True:
            r = requests.get(f"{BASE_URL}/last_result/{SESSION_ID}")
            if r.status_code == 200:
                data = r.json()
                # Prüfen, ob diese Frage schon bewertet wurde
                if not is_already_evaluated(data["question"]):
                    break
            time.sleep(1)

        print("\n--- Neue Antwort erhalten ---")
        print("Frage:", data["question"])
        print("Antwort:", data["answer"])
        print("Antwortzeit:", data["response_time"], "s")

        # Bewertung
        scores = {
            "relevance": rate("Relevanz"),
            "clarity": rate("Verständlichkeit"),
            "accuracy": rate("Korrektheit"),
            "sources": rate("Quellenqualität")
        }

        # Antwortzeit bewerten
        rt = data["response_time"]
        if rt < 2:
            rt_score = 5
        elif rt < 5:
            rt_score = 4
        elif rt < 10:
            rt_score = 3
        else:
            rt_score = 1

        # Gesamtscore berechnen
        endscore = round(
            scores["relevance"] * 0.3 +
            scores["clarity"] * 0.15 +
            scores["accuracy"] * 0.25 +
            scores["sources"] * 0.15 +
            rt_score * 0.15,
            2
        )

        print("Endscore:", endscore)

        # Ergebnis speichern
        results.append({
            "session_id": SESSION_ID,
            "question": data["question"],
            "answer": data["answer"],
            "response_time": data["response_time"],
            "scores": scores,
            "response_time_score": rt_score,
            "endscore": endscore,
            "experiment": EXPERIMENT,
            "overlap": OVERLAP,
            "prompt_used": PROMPT_USED
        })

        # JSON-Datei aktualisieren
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Bewertung gespeichert in {json_filename}.\n")
        print("Bitte neue Frage im Frontend stellen...")

except KeyboardInterrupt:
    print("\nTestdurchlauf manuell beendet.")
