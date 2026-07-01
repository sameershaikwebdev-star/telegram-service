# Sameer AI Platform 2 — Telegram Service

> The first working service of **Sameer AI Platform 2**.

---

## Overview

This repository contains the **Telegram Service**, the first completed component of **Sameer AI Platform 2** — a modular AI platform designed to support multiple communication channels, AI services, authentication, notifications, databases, and web/mobile clients.

Rather than building a single large application, the platform grows incrementally with independent services that can evolve without affecting one another. The Telegram Service is the first completed module.

---

## Features

- Telegram Bot API via **webhooks** (Flask)
- **Groq LLM** integration — Llama 3.3 70B, free tier
- **MongoDB Atlas** or **SQLite** conversation history (switchable via `DB_BACKEND`)
- Per-chat context window with configurable history depth
- `/start` and `/reset` commands
- Graceful error handling — no silent failures
- **Docker** support

---

## Quick Start

### 1. Get your credentials

| Credential | Where |
|---|---|
| Telegram Bot Token | Message **@BotFather** → `/newbot` |
| Groq API Key | [console.groq.com/keys](https://console.groq.com/keys) — free tier |
| MongoDB URI *(optional)* | [mongodb.com/atlas](https://www.mongodb.com/atlas) — free cluster |

### 2. Configure

```bash
cp .env.example .env
# Open .env and fill in TELEGRAM_BOT_TOKEN and GROQ_API_KEY
```

### 3. Install and run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 8000
```

### 4. Expose locally and register webhook

Telegram requires a public HTTPS URL. Use [ngrok](https://ngrok.com) for local testing:

```bash
ngrok http 8000
python scripts/set_webhook.py https://your-ngrok-url.ngrok-free.app
```

Message your bot — it should reply using Groq.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | — | From @BotFather |
| `GROQ_API_KEY` | ✅ | — | From console.groq.com/keys |
| `DB_BACKEND` | — | `sqlite` | `sqlite` or `mongodb` |
| `MONGODB_URI` | if mongodb | — | Atlas connection string |
| `TELEGRAM_WEBHOOK_SECRET` | — | auto-generated | Secret path segment in webhook URL |
| `GROQ_MODEL` | — | `llama-3.3-70b-versatile` | Any Groq-supported model |
| `HISTORY_LIMIT` | — | `10` | Messages sent to LLM as context |
| `DB_PATH` | — | `bot.db` | SQLite file path |

---

## Project Structure

```
services/telegram-service/
├── app.py                  # Flask app, webhook route, health check
├── bot/
│   ├── config.py           # Env-var driven configuration
│   ├── db.py               # Storage backend (SQLite or MongoDB, same API)
│   ├── handlers.py         # Command routing and conversational flow
│   ├── llm.py              # Groq API client
│   └── telegram.py         # Telegram Bot API client
├── scripts/
│   └── set_webhook.py      # One-off helper to register the webhook URL
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Docker

```bash
docker build -t telegram-service .
docker run -p 8000:8000 --env-file .env telegram-service
```

After deploying, re-run `scripts/set_webhook.py` with your real public URL.

---

## Platform Vision

Sameer AI Platform 2 is designed to grow into a full multi-service ecosystem:

```
Telegram / WhatsApp / Web / Mobile
              │
              ▼
     API Gateway (Spring Boot)
              │
   ┌──────────┼──────────────┐
   │          │              │
   ▼          ▼              ▼
Telegram   AI Service   WhatsApp
Service                  Service
   │          │              │
   └──────────┼──────────────┘
              │
   ┌──────────┼──────────────┐
   │          │              │
   ▼          ▼              ▼
Database   Auth         Notification
Service    Service       Service
```

### Roadmap

| Phase | Service | Status |
|-------|---------|--------|
| 1 | Telegram Service | ✅ Complete |
| 2 | Spring Boot API Gateway | 🚧 Planned |
| 3 | AI Service | 🚧 Planned |
| 4 | Database Service | 🚧 Planned |
| 5 | WhatsApp Service | 🚧 Planned |
| 6 | Authentication Service | 🚧 Planned |
| 7 | Notification Service | 🚧 Planned |
| 8 | React Dashboard | 🚧 Planned |
| 9 | Mobile Application | 🚧 Planned |
| 10 | Kubernetes Deployment | 🚧 Planned |

### Technology Stack

| Layer | Current | Planned |
|-------|---------|---------|
| Backend | Python, Flask | Spring Boot, FastAPI, Node.js |
| AI | Groq (Llama) | Local LLMs, vision models |
| Database | MongoDB Atlas, SQLite | Vector DB, Redis |
| Frontend | — | React, Flutter |
| Infrastructure | Docker | Docker Compose, Kubernetes, Nginx |

---

## Security

- Never hardcode secrets — all credentials live in `.env` (gitignored)
- If a token is ever pasted into a chat, screenshot, or commit: **revoke it immediately**
  - Telegram: @BotFather → `/mybots` → API Token → Revoke
  - Groq: console.groq.com → delete and regenerate the key
- The webhook URL includes a random secret so it cannot be triggered by arbitrary requests

---

## Philosophy

This project follows a **modular-first** architecture. Instead of splitting everything into microservices from day one, the platform starts with a single working service and expands as new functionality is needed. This provides a stable foundation while maintaining a clear migration path toward a scalable distributed architecture.

---

## License

MIT
