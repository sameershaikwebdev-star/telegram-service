# Telegram LLM Bot (Python, Groq, SQLite, Webhooks)

A Telegram bot that holds a real conversation using a **free, hosted LLM via
Groq** (OpenAI-compatible API, generous free tier, serves open models like
Llama), persists per-chat conversation history in **SQLite**, and receives
messages via a **webhook** (Flask) rather than polling.

Built to demonstrate: Telegram Bot API integration, webhook handling,
conversation-state storage, and LLM integration — in Python.

## Architecture

```
Telegram → POST /webhook/<secret> → Flask (app.py)
                                        │
                                        ▼
                              bot/handlers.py (routes commands, orchestrates)
                                   │              │
                                   ▼              ▼
                          bot/db.py (SQLite)  bot/llm.py (Groq)
                                   │
                                   ▼
                          bot/telegram.py (sendMessage back to user)
```

- `app.py` — Flask app, webhook route, health check.
- `bot/config.py` — env-var driven config.
- `bot/db.py` — SQLite storage for per-chat message history.
- `bot/llm.py` — calls Groq's chat completions API.
- `bot/telegram.py` — thin Telegram Bot API client.
- `bot/handlers.py` — ties it together: slash commands (`/start`, `/reset`)
  and the main conversational flow.
- `scripts/set_webhook.py` — one-off helper to register your webhook URL.

## Setup

### 1. Create your Telegram bot

Message **@BotFather** on Telegram → `/newbot` → follow prompts → copy the
token. Keep it secret — never paste it into code, chat, or commits.

### 2. Get a free Groq API key

Sign up at [console.groq.com](https://console.groq.com/keys) and create an
API key. Free tier is rate-limited but ample for a personal bot.

### 3. Configure environment

```bash
cp .env.example .env
# edit .env: paste TELEGRAM_BOT_TOKEN, GROQ_API_KEY
```

`.env` is gitignored — your secrets never get committed.

### 4. Install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run locally

```bash
flask --app app run --port 8000
```

Telegram webhooks require a **public HTTPS URL**, so for local testing expose
your local server with a tunnel, e.g. [ngrok](https://ngrok.com):

```bash
ngrok http 8000
```

Then register the webhook (use the `https://...ngrok-free.app` URL ngrok gives you):

```bash
python scripts/set_webhook.py https://your-ngrok-url.ngrok-free.app
```

Message your bot on Telegram — it should reply using Groq.

### 6. Commands

- `/start` — greeting
- `/reset` — clears your conversation history for that chat

## Deploying for real

`Dockerfile` is included for containerized deployment (Render, Railway,
Fly.io, a VPS, etc.) — all of which have free tiers suitable for this. Since
Groq is a hosted API, there's no extra service to run alongside your bot
(unlike a local-model setup).

```bash
docker build -t telegram-llm-bot .
docker run -p 8000:8000 --env-file .env telegram-llm-bot
```

After deploying, re-run `scripts/set_webhook.py` with your real public URL.

## Security notes

- Never commit `.env` (it's gitignored).
- Never paste your bot token or Groq API key into chat, screenshots, or
  commits — if either leaks, rotate it immediately (BotFather → `/mybots` →
  API Token → Revoke; Groq console → delete/regenerate the key).
- The webhook path includes a random secret (`TELEGRAM_WEBHOOK_SECRET`) so
  it can't be triggered by random requests guessing `/webhook`.
- `bot.db` (SQLite file) is gitignored — it will contain real conversation
  content once you run the bot.

## JD skills this demonstrates

- Telegram Bot API integration (webhooks, not polling)
- Backend bot logic in Python
- REST API integration with async-style request/response handling
- SQLite for conversation state
- LLM API integration (Groq, OpenAI-compatible) with prompt design
- Containerized deployment (Docker)
- Reliability: errors are caught, logged, and reported back to the user
  rather than failing silently