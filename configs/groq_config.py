import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is required.")

LLM_CONFIG = [{
    "model": GROQ_MODEL,
    "api_key": GROQ_API_KEY,
    "api_type": "groq"
}]
