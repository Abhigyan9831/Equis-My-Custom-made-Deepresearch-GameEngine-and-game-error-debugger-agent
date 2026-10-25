"""
================================================================================
BOILERPLATE: Cloud Persistent Multi-Turn Memory (Upstash Redis + SQLite Fallback)
Stack: 100% Free Cloud Managed Redis (Upstash) with zero infrastructure cost.
Use Case: Persists multi-turn conversation threads across server restarts and devices.
================================================================================
"""
import json
import time
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from app.services.cache import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

DB_PATH = Path("data/memory.sqlite")


def init_local_fallback_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL NOT NULL
            );
        """)
        conn.commit()


init_local_fallback_db()


def add_turn(session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
    """
    Store turn in Cloud Redis list (Key: 'ged:v1:mem:<session_id>')
    with local SQLite fallback.
    """
    turn_data = {
        "role": role,
        "content": content,
        "created_at": time.time(),
        "metadata": metadata or {}
    }
    payload = json.dumps(turn_data)

    # 1. Primary: Cloud Upstash Redis
    try:
        r = get_redis()
        key = f"ged:v1:mem:{session_id}"
        r.rpush(key, payload)
        # 7-day TTL on thread history
        r.expire(key, 604800)
        return
    except Exception as e:
        logger.warning(f"Cloud Redis memory write failed, falling back to SQLite: {e}")

    # 2. Fallback: Local SQLite
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO conversation_turns (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, time.time())
        )
        conn.commit()


def get_conversation_history(session_id: str, limit: int = 6) -> List[Dict[str, str]]:
    """
    Fetch recent turns from Cloud Redis with SQLite fallback.
    """
    # 1. Primary: Cloud Upstash Redis
    try:
        r = get_redis()
        key = f"ged:v1:mem:{session_id}"
        # Fetch last N items
        raw_turns = r.lrange(key, -limit, -1)
        if raw_turns:
            turns = [json.loads(t) for t in raw_turns]
            return [{"role": t["role"], "content": t["content"]} for t in turns]
    except Exception as e:
        logger.warning(f"Cloud Redis memory read failed, falling back to SQLite: {e}")

    # 2. Fallback: Local SQLite
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT role, content FROM conversation_turns WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_session_memory(session_id: str):
    """Clear memory for a session in Cloud Redis and local fallback."""
    try:
        r = get_redis()
        r.delete(f"ged:v1:mem:{session_id}")
    except Exception as e:
        logger.warning(f"Cloud Redis delete failed: {e}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM conversation_turns WHERE session_id = ?", (session_id,))
        conn.commit()
