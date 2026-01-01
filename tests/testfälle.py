import json
import os

# Verzeichnis, in dem die Testfälle gespeichert werden
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "testcases2.json")

# Testfälle für den Chatbot

testcases = [
    {"ID": "T1", "question": "Was ist für die Stand-up meetings im HS 2025 geplant?", 
     "requirements": ["F1", "F2", "F3", "F6"]},    
    {"ID": "T2", "question": "Welche rechtlichen Fragen bestehen bei KI in der Schweiz laut dem Edu-Lab?", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T3", "question": "wird hier auch auf den Eu Act eingangen?", 
     "requirements": ["F1", "F2", "F3", "F6", "F7", "F8"]},
    {"ID": "T4", "question": "was sind die Schwerpunkte dieses blogs", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]}, 
    {"ID": "T5", "question": "Wann war die letzte US-Wahl", 
     "requirements": ["F3", "F4", "F6"]}, 
    {"ID": "T6", "question": "Um was ging es beim Stand-Up-Meeting vom 2. Mai 2023 FS?", 
     "requirements": ["F1", "F2", "F3", "F6", "F8"]},   
    {"ID": "T7", "question": "Gibt es einen Beitrag zu Plagiatsoftware?",  
     "requirements": ["F1", "F3", "F2", "F6"]},
    {"ID": "T8", "question": "Was ist ein Plagiat?",  
     "requirements": ["F1", "F3", "F2", "F6", "F8"]},       
    {"ID": "T9", "question": "Gibt es Informationen zu den Modulendprüfungen auf dem Blog?", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T10", "question": "Welche neuen Werte oder Kompetenzen erwartet das Edu-Lab in KI-gestützter Lehre?", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T11", "question": "Are there any survey results on here?", 
     "requirements": ["F5", "F4", "F6"]},
    {"ID": "T12", "question": "Um was geht es in den Experimentiermodulen", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]},
    {"ID": "T13", "question": "Wie wird im Edu-I Lab Wissensaustausch zwischen Dozierenden organisiert?", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T14", "question": "Welche didaktischen Herausforderungen entstehen durch KI?", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T15", "question": "Welche Blockchain-Projekte hat das Edu-Lab durchgeführt?", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T16", "question": "was kannst du mir zum AI Thesis Coach erzählen?", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]},
    {"ID": "T17", "question": "Wer ist Bundesrat der Schweiz?", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T18", "question": "Are there some discussions about ChatGPT on the blog?", 
     "requirements": ["F5", "F4", "F6"]},
    {"ID": "T19", "question": "Welche personenbezogenen Daten von Studierenden werden im Edu-Lab gespeichert?", 
     "requirements": ["F3", "F4"]},
    {"ID": "T20", "question": "Wann beginnt das Frühlingssemester 2026?", 
     "requirements": ["F3", "F4"]},
    {"ID": "T21", "question": "dwad hgfdf dsfa", 
     "requirements": ["F3", "F7"]},
]

# JSON-Datei speichern
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(testcases, f, ensure_ascii=False, indent=4)

print(f"Testfälle wurden erstellt und gespeichert in '{OUTPUT_FILE}'")
