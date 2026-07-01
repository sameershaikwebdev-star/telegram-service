"""
Minimal Telegram Bot API client (just what this bot needs).
"""
import logging

import requests

from bot.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(chat_id: int, text: str):
    response = requests.post(
        f"{API_BASE}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30,
    )
    if response.status_code != 200:
        logger.error("Telegram sendMessage failed (%s): %s", response.status_code, response.text)
    return response


def send_chat_action(chat_id: int, action: str = "typing"):
    requests.post(
        f"{API_BASE}/sendChatAction",
        json={"chat_id": chat_id, "action": action},
        timeout=10,
    )


def set_webhook(url: str) -> dict:
    response = requests.post(f"{API_BASE}/setWebhook", json={"url": url}, timeout=30)
    response.raise_for_status()
    return response.json()


def delete_webhook() -> dict:
    response = requests.post(f"{API_BASE}/deleteWebhook", timeout=30)
    response.raise_for_status()
    return response.json()


def get_webhook_info() -> dict:
    response = requests.get(f"{API_BASE}/getWebhookInfo", timeout=30)
    response.raise_for_status()
    return response.json()