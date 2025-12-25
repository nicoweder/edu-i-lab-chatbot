import json

# ===============================
# Bereinigte Testfälle (ohne Namen)
# ===============================
testcases = [
    {"ID": "T1", "question": "Wann sind die Stand-Up-Meetings im HS 2025 geplant?", 
     "expected": "Der Chatbot sollte die „Vorläufige Agenda Stand-Ups HS 2025“ nennen (Datum, Themen, ggf. Links).", 
     "requirements": ["F1", "F2", "F3", "F6"]},    
    {"ID": "T2", "question": "Welche rechtlichen Fragen bestehen bei KI in der Schweiz laut dem Edu-Lab?", 
     "expected": "Darstellung von technischen, regulatorischen und rechtlichen Aspekten (Datenschutz, Cloud, AGB).", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T3", "question": "wird hier auch auf den Eu Act eingangen?", 
     "expected": "Darstellung von technischen, regulatorischen und rechtlichen Aspekten (Datenschutz, Cloud, AGB).", 
     "requirements": ["F1", "F2", "F3", "F6", "F7", "F8"]},
    {"ID": "T4", "question": "Welche neuen Lerformate diskutiert das Edu-Lab im Bog?", 
     "expected": "Übersicht neuer Lehrformate: Hybridunterricht, KI-Nutzung, Stand-Ups etc.", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]}, 
    {"ID": "T5", "question": "Wann war die letzte US-Wahl", 
     "expected": "Zukunftsperspektiven: Hybrid, KI-gestützt, personalisierte Lehre.", 
     "requirements": ["F3", "F4", "F6"]}, 
    {"ID": "T6", "question": "Um was ging es beim stand up meeting 2024 HS?", 
     "expected": "Reflexionen in Stand-Ups und Blogartikeln.", 
     "requirements": ["F1", "F2", "F3", "F6", "F8"]},   
    {"ID": "T7", "question": "Gibt es einen Bitrag zu Plagitsoftware?",  
     "expected": "Liste der Agenda-Punkte.", 
     "requirements": ["F1", "F3", "F2", "F6"]},
    {"ID": "T8", "question": "Was ist ein Plagiat?",  
     "expected": "Liste der Agenda-Punkte.", 
     "requirements": ["F1", "F3", "F2", "F6", "F8"]},       
    {"ID": "T9", "question": "Gibt es Informationen zu den Modulendprüfungen auf dem Blog?", 
     "expected": "Reflexionen in Stand-Ups und Blogartikeln.", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T10", "question": "Welche neuen Werte oder Kompetenzen erwartet das Edu-Lab in KI-gestützter Lehre?", 
     "expected": "Selbstverantwortung, Transparenz, digitale Medienkompetenz.", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T11", "question": "Is there something about the edu lab brochure here?", 
     "expected": "Der Chatbot gibt eine Antwort auf Englisch, ohne Sprachen zu mischen, basierend auf englischen Übersetzungen der Inhalte.", 
     "requirements": ["F5", "F4", "F6"]},
    {"ID": "T12", "question": "Sag mir etwas zu den Expermentiermodulen", 
     "expected": "Beispiele aus Pilotprojekten.", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]},
    {"ID": "T13", "question": "Wie wird im Edu-Lab Wissensaustausch zwischen Dozierenden organisiert?", 
     "expected": "Stand-Ups, Workshops, Peer-Feedback-Sessions.", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T14", "question": "Welche didaktischen Herausforderungen entstehen durch KI?", 
     "expected": "Anleitung, Bewertung, Täuschungssicherheit.", 
     "requirements": ["F1", "F2", "F3", "F6"]},
    {"ID": "T15", "question": "Welche Blockchain-Projekte hat das Edu-Lab 2023 durchgeführt?", 
     "expected": "Keine Informationen vorhanden.", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T16", "question": "Wie kann der AI Thesis Cach bei wissenschaftlicher Arbeiten helfen?", 
     "expected": "Gliederungsvorschläge, Kohärenz-Feedback.", 
     "requirements": ["F1", "F2", "F3", "F6", "F7"]},
    {"ID": "T17", "question": "Wer ist Bundesrat der Schweiz", 
     "expected": "Zukunftsperspektiven: Hybrid, KI-gestützt, personalisierte Lehre.", 
     "requirements": ["F3", "F4", "F6"]},
    {"ID": "T18", "question": "Are there some discussions about chatGPT on the blog?", 
     "expected": "Der Chatbot gibt eine Antwort auf Englisch, ohne Sprachen zu mischen, basierend auf englischen Übersetzungen der Inhalte.", 
     "requirements": ["F5", "F4", "F6"]},
    {"ID": "T19", "question": "Welche personenbezogenen Daten von Studierenden werden im Edu-Lab gespeichert?", 
     "expected": "Der Blog enthält keine Informationen über personenbezogene Daten von Studierenden. Dazu liegen keine Angaben vor.", 
     "requirements": ["F3", "F4"]},
    {"ID": "T19", "question": "Wann beginnt das Herbstsemester 2026?", 
     "expected": "Der Blog enthält keine Informationen über personenbezogene Daten von Studierenden. Dazu liegen keine Angaben vor.", 
     "requirements": ["F3", "F4"]},
]

# ===============================
# JSON-Datei speichern
# ===============================
with open("testcases.json", "w", encoding="utf-8") as f:
    json.dump(testcases, f, ensure_ascii=False, indent=4)

print("✅ testcases.json wurde erstellt!")
