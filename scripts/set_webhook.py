"""
One-off helper: register your public webhook URL with Telegram.

Usage:
    python scripts/set_webhook.py https://your-public-host.example.com

This appends the secret path automatically.
"""
import sys

from bot.config import TELEGRAM_WEBHOOK_SECRET
from bot.telegram import get_webhook_info, set_webhook


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_webhook.py https://your-public-host.example.com")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    full_url = f"{base_url}/webhook/{TELEGRAM_WEBHOOK_SECRET}"

    result = set_webhook(full_url)
    print("setWebhook response:", result)

    info = get_webhook_info()
    print("getWebhookInfo:", info)


if __name__ == "__main__":
    main()