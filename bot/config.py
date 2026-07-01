"""
Configuration loaded from environment variables.
Copy .env.example to .env and fill in your real values — never commit .env.
"""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Secret path segment for the webhook URL, e.g. /webhook/<this>.
# Generates a random one if you don't set it, so the URL isn't guessable.
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET") or secrets.token_urlsafe(24)

# Groq: free-tier, OpenAI-compatible API serving open models (Llama, etc.)
# Get a free key at https://console.groq.com/keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

MONGODB_URI = os.environ.get("MONGODB_URI", "")

DB_PATH = os.environ.get("DB_PATH", "bot.db")

HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "10"))

SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a helpful, concise assistant chatting with a user over Telegram. "
    "Keep replies short and conversational unless asked for detail.",
)

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is not set. Add it to your .env file (see .env.example)."
    )

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
        "and add it to your .env file."
    )
if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not set. Add it to your .env file (see .env.example)."
    )