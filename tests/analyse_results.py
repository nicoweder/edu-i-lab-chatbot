import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# Pfade
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# ===============================
# Alle Result-Dateien laden
# ===============================
all_results = []

for file in os.listdir(RESULTS_DIR):
    if file.endswith(".json"):
        path = os.path.join(RESULTS_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                row["_file"] = file
                all_results.append(row)

df = pd.DataFrame(all_results)

print(f"\n📊 {len(df)} Einträge aus {len(df['_file'].unique())} Experimenten geladen.\n")

# ===============================
# Metriken extrahieren
# ===============================
df["relevance"] = df["bewertung"].apply(lambda x: x["relevance"])
df["clarity"] = df["bewertung"].apply(lambda x: x["clarity"])
df["accuracy"] = df["bewertung"].apply(lambda x: x["accuracy"])
df["sources"] = df["bewertung"].apply(lambda x: x["sources"])

# ===============================
# Aggregation pro Experiment
# ===============================
group_cols = ["experiment", "overlap", "prompt"]

summary = (
    df.groupby(group_cols)
    .agg(
        avg_endscore=("endscore", "mean"),
        avg_relevance=("relevance", "mean"),
        avg_accuracy=("accuracy", "mean"),
        avg_clarity=("clarity", "mean"),
        avg_sources=("sources", "mean"),
        avg_response_time=("dauer_s", "mean"),
        n_questions=("ID", "count")
    )
    .reset_index()
    .sort_values(by="avg_endscore", ascending=False)
)

print("\n🏆 BESTE KONFIGURATIONEN:")
print(summary)

# ===============================
# Beste Konfiguration ausgeben
# ===============================
best = summary.iloc[0]
print("\n✅ BESTES SETUP:")
print(best)

# ===============================
# Visualisierung
# ===============================
plt.figure(figsize=(10, 5))
plt.barh(
    summary["experiment"] + " | " + summary["prompt"],
    summary["avg_endscore"]
)
plt.xlabel("Durchschnittlicher Endscore")
plt.ylabel("Experiment")
plt.title("Vergleich der Experimente")
plt.gca().invert_yaxis()
plt.tight_layout()

# Plot speichern
plot_path = os.path.join(RESULTS_DIR, "experiment_comparison.png")
plt.savefig(plot_path)
plt.show()

print(f"\n📈 Plot gespeichert unter: {plot_path}")
