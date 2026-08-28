from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterable, List


def connect(dsn: str):
    try:
        import psycopg

        return psycopg.connect(dsn)
    except ImportError:
        pass

    try:
        import psycopg2

        return psycopg2.connect(dsn)
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Install either 'psycopg[binary]' or 'psycopg2-binary' to use database access."
        ) from exc


def fetch_all(conn, sql: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    params = params or {}
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        if cursor.description is None:
            return []
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        result: List[Dict[str, Any]] = []
        for row in rows:
            result.append({col: value for col, value in zip(columns, row)})
        return result
    finally:
        cursor.close()


@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

