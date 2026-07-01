"""
Core update-handling logic: receives a Telegram update, manages conversation
state in SQLite, calls the LLM, and replies.
"""
import logging

from bot import db
from bot.llm import LLMError, generate_reply
from bot.telegram import send_chat_action, send_message

logger = logging.getLogger(__name__)

COMMANDS = {}


def command(name):
    def decorator(fn):
        COMMANDS[name] = fn
        return fn
    return decorator


@command("/start")
def cmd_start(chat_id: int, _args: str):
    send_message(
        chat_id,
        "Hi! I'm an LLM-powered bot (running on Groq). "
        "Just send me a message. Use /reset to clear our conversation history.",
    )


@command("/reset")
def cmd_reset(chat_id: int, _args: str):
    db.clear_history(chat_id)
    send_message(chat_id, "Conversation history cleared.")


def handle_update(update: dict):
    message = update.get("message")
    if not message:
        # Ignore non-message updates (edited messages, callback queries, etc.)
        return

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if chat_id is None or not text:
        return

    # Slash command?
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd_name = parts[0].split("@")[0]  # strip @botname if present
        args = parts[1] if len(parts) > 1 else ""
        handler = COMMANDS.get(cmd_name)
        if handler:
            handler(chat_id, args)
        else:
            send_message(chat_id, f"Unknown command: {cmd_name}")
        return

    send_chat_action(chat_id, "typing")

    db.save_message(chat_id, "user", text)
    history = db.get_recent_history(chat_id)

    try:
        reply = generate_reply(history)
    except LLMError as exc:
        logger.error("LLM error: %s", exc)
        send_message(chat_id, f"Sorry, I couldn't generate a reply: {exc}")
        return

    db.save_message(chat_id, "assistant", reply)
    send_message(chat_id, reply)