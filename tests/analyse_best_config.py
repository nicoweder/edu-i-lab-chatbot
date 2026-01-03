import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ermittlung des Basisverzeichnisses des aktuellen Skripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definition des Pfades zur auszuwertenden JSON-Ergebnisdatei
JSON_PATH = os.path.join(BASE_DIR, "results", "paragraph_over0_FINAL_PROMPT_2.json")

# Laden der JSON-Datei in den Arbeitsspeicher
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Überführung der geladenen Daten in ein Pandas DataFrame
df = pd.DataFrame(data)

# Extraktion der einzelnen Bewertungsdimensionen aus der Score-Struktur
df["relevance"] = df["scores"].apply(lambda x: x["relevance"])
df["clarity"] = df["scores"].apply(lambda x: x["clarity"])
df["accuracy"] = df["scores"].apply(lambda x: x["accuracy"])
df["sources"] = df["scores"].apply(lambda x: x["sources"])
df["response_time_score"] = df["response_time_score"]

# Berechnung der Durchschnittswerte aller Bewertungsdimensionen
avg_scores = df[
    ["relevance", "clarity", "accuracy", "sources", "response_time_score", "endscore"]
].mean()

print("\nDurchschnittswerte:")
print(avg_scores)

# Erstellung einer Balkengrafik zur Darstellung der durchschnittlichen Bewertungen
sns.set(style="whitegrid")
plt.figure(figsize=(9, 5))

bars = plt.bar(
    avg_scores.index,
    avg_scores.values,
    color=sns.color_palette("Blues", len(avg_scores))
)

# Festlegung sinnvoller Grenzen für die y-Achse entsprechend der Skala
plt.ylim(0, 5.2)

# Anzeige der exakten Durchschnittswerte oberhalb der Balken
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        min(height + 0.08, 5.05),
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=10
    )

# Beschriftung der Achsen sowie Festlegung des Diagrammtitels
plt.ylabel("Durchschnittlicher Score (1–5)")
plt.title("Durchschnittliche Bewertung – paragraph_over0_FINAL_PROMPT_2")

plt.tight_layout()

# Speicherung der Visualisierung als hochauflösende Bilddatei
output_path = os.path.join(
    BASE_DIR,
    "results",
    "avg_scores_paragraph_over0_FINAL_PROMPT_2.png"
)

plt.savefig(output_path, dpi=300)
plt.show()

print(f"\nPlot gespeichert unter:\n{output_path}")
