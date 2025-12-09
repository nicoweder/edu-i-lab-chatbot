import json
import time
import csv
import os
from search_and_answer import RAGChatSession, client, index, metadata

# ===============================
# 🔍 Testfälle laden
# ===============================
TESTFILE = os.path.join("..", "tests", "testcases.json")  # Pfad relativ zum src-Ordner

with open(TESTFILE, "r", encoding="utf-8") as f:
    testcases = json.load(f)

print(f"{len(testcases)} Testfälle geladen.\n")

# ===============================
# ⚖️ Bewertungsfunktion
# ===============================
def evaluate_answer_manual():
    """
    Fragt den Nutzer manuell nach den Scores für Relevance, Clarity und Fact Score.
    """
    while True:
        try:
            relevance = int(input("Relevance (1-5): "))
            clarity = int(input("Clarity (1-5): "))
            fact = int(input("Fact Score (1-5): "))
            if all(1 <= v <= 5 for v in [relevance, clarity, fact]):
                return relevance, clarity, fact
            else:
                print("Bitte nur Zahlen von 1 bis 5 eingeben.")
        except ValueError:
            print("Ungültige Eingabe, bitte Zahlen verwenden.")

# ===============================
# 🧪 Tests ausführen
# ===============================
session = RAGChatSession(client, index, metadata, top_k=5)
results = []

for idx, testcase in enumerate(testcases):
    frage = testcase["question"]
    print(f"\n({idx+1}/{len(testcases)}) Testfall {testcase['ID']}: {frage}")

    start = time.time()
    try:
        res = session.ask(frage)
    except Exception as e:
        print(f"⚠️ Fehler bei der Frage: {e}")
        res = {"answer": "", "sources": []}
    end = time.time()
    duration = round(end - start, 3)

    # Antwort anzeigen
    print("\nAntwort des Chatbots:")
    print(res.get("answer", "Keine Antwort erhalten."))
    print("\nQuellen:")
    for s in res.get("sources", []):
        print(f"- {s.get('title')} ({s.get('score')}) → {s.get('url')}")

    # Manuelle Bewertung
    relevance, clarity, fact = evaluate_answer_manual()

    results.append({
        "ID": testcase["ID"],
        "frage": frage,
        "antwort": res.get("answer", ""),
        "quellen": res.get("sources", []),
        "dauer_s": duration,
        "bewertung": {
            "relevance": relevance,
            "clarity": clarity,
            "accuracy": fact
        }
    })

    print(f"→ Dauer: {duration}s | Bewertung gespeichert. Weiter zur nächsten Frage...\n")

# ===============================
# 💾 Ergebnisse speichern
# ===============================
# JSON
with open("test_results_manual.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# CSV
with open("test_results_manual.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Frage", "Antwort", "Quellen", "Antwortzeit (s)",
                     "Relevance", "Clarity", "Fact Score"])

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
            r["bewertung"]["accuracy"]
        ])

print("\n✅ Alle Testfälle bearbeitet. Ergebnisse gespeichert in test_results_manual.json und test_results_manual.csv.")
