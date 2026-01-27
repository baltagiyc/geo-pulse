"""Access code quota management via SQLite."""

import os
import sqlite3

from src.core.config import get_access_code_db_path


def _ensure_db_directory(db_path: str) -> None:
    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)


def _initialize_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS access_code_usage (
            access_code TEXT PRIMARY KEY,
            audits_used INTEGER NOT NULL DEFAULT 0
        )
        """
    )


def consume_access_code_quota(access_code: str, max_audits: int) -> tuple[bool, int]:
    """
    Increment usage for an access code if quota allows it.

    Returns (allowed, remaining_after).
    """
    if not access_code:
        return True, max_audits
    if max_audits <= 0:
        return False, 0

    db_path = get_access_code_db_path()
    _ensure_db_directory(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        _initialize_db(conn)

        row = conn.execute(
            "SELECT audits_used FROM access_code_usage WHERE access_code = ?",
            (access_code,),
        ).fetchone()
        audits_used = row[0] if row else 0

        if audits_used >= max_audits:
            return False, 0

        new_used = audits_used + 1
        if row:
            conn.execute(
                "UPDATE access_code_usage SET audits_used = ? WHERE access_code = ?",
                (new_used, access_code),
            )
        else:
            conn.execute(
                "INSERT INTO access_code_usage (access_code, audits_used) VALUES (?, ?)",
                (access_code, new_used),
            )

        remaining = max(max_audits - new_used, 0)
        return True, remaining
