"""
Telegram LLM Bot — Flask webhook entry point.

Local dev:
    flask --app app run --port 8000
    # in another terminal, expose it publicly (e.g. with ngrok) and run
    # scripts/set_webhook.py to point Telegram at it.

Production: see README.md / Dockerfile.
"""
import logging
import os

from flask import Flask, jsonify, request

from bot import db
from bot.config import TELEGRAM_WEBHOOK_SECRET
from bot.handlers import handle_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db.init_db()


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route(f"/webhook/{TELEGRAM_WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)
    if not update:
        return jsonify({"ok": False, "error": "no payload"}), 400

    try:
        handle_update(update)
    except Exception:
        logger.exception("Failed to handle update")
        # Return 200 anyway so Telegram doesn't retry-storm us; the error
        # is logged for us to inspect.
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)