import os
import json
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import pickle
import time
import logging

from prompts import FINAL_PROMPT_1, FINAL_PROMPT_2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPERIMENT = "chunks_paragraph_no_overlap" # Hier Namen der erstellten Idizes, die getestet werden sollen angeben

INDEX_DIR = os.path.join(BASE_DIR, "data", "indices", EXPERIMENT)
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.pkl")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY nicht gesetzt (.env fehlt?)")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.info(f"Lade FAISS Index aus {INDEX_PATH} ...")
index = faiss.read_index(INDEX_PATH)

logging.info(f"Lade Metadaten aus {METADATA_PATH} ...")
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

logging.info(f"Index und Metadaten erfolgreich geladen ({len(metadata)} Einträge)")


class RAGChatSession:
    def __init__(
        self,
        client,
        index,
        metadata,
        top_k=5,
        max_messages=30,
        context_char_limit=4000,
        final_prompt_variant=1
    ):
        """
        Initialisiert eine neue RAG-Chat-Session mit FAISS-Index, Metadaten
        sowie konfigurierbaren Parametern für Kontextlänge und Prompt-Variante.
        """
        self.client = client
        self.index = index
        self.metadata = metadata
        self.top_k = top_k
        self.history = []
        self.last_context = ""
        self.last_all_links = []
        self.last_inline_sources = []
        self.start_time = time.time()
        self.max_messages = max_messages
        self.context_char_limit = context_char_limit
        self.final_prompt_variant = 2

    def reset(self):
        """
        Setzt den Chatverlauf sowie alle gespeicherten Kontextinformationen zurück
        und startet die Sitzungszeit neu.
        """
        self.history = []
        self.last_context = ""
        self.last_all_links = []
        self.last_inline_sources = []
        self.start_time = time.time()
        logging.info("Chatverlauf wurde zurückgesetzt.")

    def check_expiry(self):
        """
        Prüft, ob die maximale Sitzungsdauer von 24 Stunden überschritten wurde
        und setzt den Chatverlauf gegebenenfalls zurück.
        """
        if (time.time() - self.start_time) / 3600 >= 24:
            logging.info("Maximale Sitzungsdauer erreicht. Chatverlauf wird zurückgesetzt.")
            self.reset()

    def check_max_messages(self):
        """
        Prüft, ob die maximale Anzahl gespeicherter Nachrichten überschritten wurde
        und setzt den Chatverlauf gegebenenfalls zurück.
        """
        if len(self.history) >= self.max_messages:
            logging.info(f"Maximale Anzahl von {self.max_messages} Nachrichten erreicht.")
            self.reset()

    def search(self, query):
        """
        Erstellt ein Embedding für die Nutzeranfrage und führt eine semantische
        Suche im FAISS-Index durch.
        """
        try:
            embedding = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=query
            ).data[0].embedding
        except Exception as e:
            logging.error(f"Fehler bei der Embedding-Erstellung: {e}")
            return []

        xq = np.array([embedding], dtype=np.float32)
        try:
            distances, indices = self.index.search(xq, self.top_k)
        except Exception as e:
            logging.error(f"Fehler bei der FAISS-Suche: {e}")
            return []

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                m = self.metadata[idx].copy()
                m["score"] = float(distances[0][i])
                results.append(m)
        return results

    def build_context(self, results):
        """
        Erstellt aus den Suchergebnissen einen zusammenhängenden Kontexttext
        sowie eine Liste aller enthaltenen Referenzlinks.
        """
        context_blocks = []
        all_links = []
        for r in results:
            context_blocks.append(
                f"---\nTitel: {r['title']}\nText:\n{r['chunk_text']}\n"
            )
            for link in r.get("links", []):
                all_links.append({"anchor": link["anchor"], "url": link["href"]})

        context_text = "\n".join(context_blocks)

        if len(context_text) > self.context_char_limit:
            context_text = context_text[-self.context_char_limit:]

        return context_text, all_links

    def safe_chat_completion(self, prompt, retries=3, temperature=0.1):
        """
        Führt einen Chat-Completion-Aufruf mit definierter Anzahl an
        Wiederholungsversuchen bei API-Fehlern aus.
        """
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logging.warning(f"API-Fehler (Versuch {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        return "Fehler beim Abrufen der Antwort."

    def ask(self, query):
        """
        Verarbeitet eine Nutzeranfrage inklusive Kontextprüfung,
        semantischer Suche, Prompt-Erstellung und Antwortgenerierung.
        """
        self.check_expiry()
        self.check_max_messages()

        history_text = "\n".join(
            [f"User: {h['user']}\nAssistant: {h['assistant']}" for h in self.history]
        )
        last_context = getattr(self, "last_context", "")
        all_links = getattr(self, "last_all_links", [])

        prompt_check = f"""
Du bist ein faktenbasierter Chatbot für den Edu-I Lab Blog der Hochschule Luzern.
Prüfe, ob die folgende Frage aus dem bisherigen Chatverlauf und dem letzten Kontext beantwortbar ist.

Chatverlauf + letzter Kontext:
{history_text}
{last_context}

Frage:
{query}

Wenn beantwortbar: Antworte kurz mit "BEANTWORTBAR"
Wenn nicht: Antworte exakt: "NICHT BEANTWORTBAR"
"""
        check_answer = self.safe_chat_completion(prompt_check, temperature=0).upper()

        if "NICHT BEANTWORTBAR" in check_answer:
            results = self.search(query)
            context, all_links = self.build_context(results)
            self.last_context = context
            self.last_all_links = all_links
            self.last_inline_sources = [
                {"title": r["title"], "url": r.get("url")} for r in results
            ]
            return_sources = True
        else:
            results = []
            context = last_context or ""
            all_links = getattr(self, "last_all_links", [])
            return_sources = True

        final_prompt_template = (
            FINAL_PROMPT_1 if self.final_prompt_variant == 1 else FINAL_PROMPT_2
        )
        prompt_final = final_prompt_template.format(
            history_text=history_text,
            query=query,
            context=context,
            links_json=json.dumps(all_links, ensure_ascii=False)
        )

        answer = self.safe_chat_completion(prompt_final, temperature=0.1)

        self.history.append({"user": query, "assistant": answer})
        inline_sources = (
            getattr(self, "last_inline_sources", []) if return_sources else []
        )

        return {
            "query": query,
            "answer": answer,
            "inline_sources": inline_sources
        }


if __name__ == "__main__":
    session = RAGChatSession(client, index, metadata, final_prompt_variant=1)

    while True:
        query = input("Frage: ")
        if query.lower() in ["exit", "quit", "stop"]:
            break

        result = session.ask(query)

        print("\nAntwort:")
        print(result["answer"])
        print("\nQuellen:")
        for s in result.get("inline_sources", []):
            print(f"- {s['title']} → {s['url']}")
