"""
Storage backend for per-chat conversation history.

Set DB_BACKEND in your .env:
    DB_BACKEND=sqlite    → uses SQLite (default, no extra setup)
    DB_BACKEND=mongodb   → uses MongoDB (set MONGODB_URI too)

The public API is identical regardless of backend:
    init_db()
    save_message(chat_id, role, content)
    get_recent_history(chat_id) -> list[{"role": ..., "content": ...}]
    clear_history(chat_id)
"""
import logging
import os

from pymongo.errors import PyMongoError

from bot.config import HISTORY_LIMIT

logger = logging.getLogger(__name__)

DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite").strip().lower()

# ---------------------------------------------------------------------------
# SQLite backend
# ---------------------------------------------------------------------------
if DB_BACKEND == "sqlite":
    import sqlite3
    from contextlib import contextmanager
    from datetime import datetime, timezone

    from bot.config import DB_PATH

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS messages (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id    INTEGER NOT NULL,
        role       TEXT    NOT NULL CHECK (role IN ('user', 'assistant')),
        content    TEXT    NOT NULL,
        created_at TEXT    NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages (chat_id, id);
    """

    @contextmanager
    def _connect():
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db():
        with _connect() as conn:
            conn.executescript(_SCHEMA)
        logger.info("SQLite DB ready at %s", DB_PATH)

    def save_message(chat_id: int, role: str, content: str):
        with _connect() as conn:
            conn.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) "
                "VALUES (?, ?, ?, ?)",
                (chat_id, role, content, datetime.now(timezone.utc).isoformat()),
            )

    def get_recent_history(chat_id: int, limit: int = HISTORY_LIMIT) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages "
                "WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit),
            ).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def clear_history(chat_id: int):
        with _connect() as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))

# ---------------------------------------------------------------------------
# MongoDB backend
# ---------------------------------------------------------------------------
elif DB_BACKEND == "mongodb":
    from datetime import datetime, timezone

    from pymongo import ASCENDING, DESCENDING, MongoClient

    from bot.config import MONGODB_URI

    if not MONGODB_URI:
        raise RuntimeError(
            "DB_BACKEND=mongodb requires MONGODB_URI to be set in your .env file.\n"
            "Example: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/"
        )

    _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

    try:
        _client.admin.command("ping")
        logger.info("Connected to MongoDB Atlas")
    except PyMongoError as e:
        logger.exception("Failed to connect to MongoDB")
        raise RuntimeError(f"MongoDB connection failed: {e}")
    _col = _client["telbot"]["messages"]

    def init_db():
        _col.create_index(
            [("chat_id", ASCENDING), ("created_at", DESCENDING)],
            background=True,
        )
        logger.info("MongoDB ready — db=telbot, collection=messages")

    def save_message(chat_id: int, role: str, content: str):
        _col.insert_one({
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "created_at": datetime.now(timezone.utc),
        })

    def get_recent_history(chat_id: int, limit: int = HISTORY_LIMIT) -> list[dict]:
        docs = list(
            _col.find(
                {"chat_id": chat_id},
                {"_id": 0, "role": 1, "content": 1},
            )
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        docs.reverse()
        return docs

    def clear_history(chat_id: int):
        _col.delete_many({"chat_id": chat_id})

# ---------------------------------------------------------------------------
# Unknown backend
# ---------------------------------------------------------------------------
else:
    raise RuntimeError(
        f"Unknown DB_BACKEND={DB_BACKEND!r}. "
        "Set DB_BACKEND to 'sqlite' or 'mongodb' in your .env file."
    )