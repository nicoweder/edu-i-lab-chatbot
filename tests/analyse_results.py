import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Basisverzeichnis und Results-Ordner
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# -----------------------------
# Alle JSON-Dateien im Ordner laden
# -----------------------------
all_results = []

for file in os.listdir(RESULTS_DIR):
    if file.endswith(".json"):
        path = os.path.join(RESULTS_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                # Dateiname als Experimentname abspeichern
                row["_experiment_file"] = file
                all_results.append(row)

if not all_results:
    print("Keine Ergebnisse gefunden.")
    exit()

df = pd.DataFrame(all_results)

# -----------------------------
# Prozent der Fragen mit Endscore ≥ 4 berechnen
# -----------------------------
percent_passed = (
    df.groupby("_experiment_file")
    .apply(lambda x: (x["endscore"] >= 4.5).sum() / len(x) * 100)
    .reset_index(name="percent_above_4")
    .sort_values(by="percent_above_4", ascending=True)
)

print("\nProzent der Fragen mit Endscore ≥ 4 pro Experiment:")
print(percent_passed)

# -----------------------------
# Balkendiagramm erstellen
# -----------------------------
sns.set(style="whitegrid")
plt.figure(figsize=(12, 7))

bars = plt.barh(
    percent_passed["_experiment_file"],      # hier werden die Dateinamen als Achsenbeschriftung verwendet
    percent_passed["percent_above_4"],
    color=sns.color_palette("Blues_d", len(percent_passed))
)

# Prozentwerte direkt auf den Balken anzeigen
for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height() / 2,
             f"{width:.1f}%", va="center", fontsize=10)

plt.xlabel("Prozent der Fragen mit Endscore ≥ 4.5")
plt.ylabel("Experiment (JSON-Datei)")
plt.title("Qualität der Experimente nach Endscore", fontsize=14, fontweight="bold")
plt.xlim(0, 100)
plt.tight_layout()

# -----------------------------
# Plot speichern und anzeigen
# -----------------------------
plot_path = os.path.join(RESULTS_DIR, "percent_above_4_by_file.png")
plt.savefig(plot_path, dpi=300)
plt.show()

print(f"\nPlot gespeichert unter: {plot_path}")
