"""
Thin client for Groq's OpenAI-compatible chat completions API.
Free tier, no local model hosting required. Get a key at
https://console.groq.com/keys
"""
import logging

import requests

from bot.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


def generate_reply(history: list[dict]) -> str:
    """
    history: list of {"role": "user"|"assistant", "content": str}, oldest first.
    Returns the assistant's reply text.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    try:
        response = requests.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("Groq request failed")
        body = getattr(exc.response, "text", "")
        raise LLMError(f"Groq API request failed: {exc} {body}") from exc

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Unexpected Groq response shape: {data}") from exc

    return content.strip()