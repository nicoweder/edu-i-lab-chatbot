import os
from dotenv import load_dotenv

# .env laden
load_dotenv()

# Key ausgeben
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ OPENAI_API_KEY gefunden:", api_key[:30] + "...")
else:
    print("❌ Kein API Key gefunden.")
