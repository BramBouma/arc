"""
lightweight document store backed by tinydb.
designed for json‑ish payloads like edgar filings,
statscan raw responses, or any semi‑structured blob.

Usage
-----
from document_store import doc_db

doc_db.insert("edgar_filings", {"cik": "0000320193", "form": "10‑K", ...})
results = doc_db.find("edgar_filings", lambda r: r["form"] == "10‑K")
"""

from pathlib import Path
from typing import Any, Callable

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

DEFAULT_PATH = Path(__file__).resolve().parent / ".." / "arc_docs.json"
DEFAULT_PATH = DEFAULT_PATH.resolve()


class _DocDB:
    def __init__(self, file_path: str | Path = DEFAULT_PATH):
        self._db = TinyDB(
            Path(file_path),
            storage=CachingMiddleware(JSONStorage),  # simple write‑back cache
            indent=2,  # human‑readable JSON
        )

    # ---------- Generic helpers ---------- #
    def _table(self, name: str):
        "Returns (and lazily creates) a TinyDB table."
        return self._db.table(name)

    # ---------- CRUD operations ---------- #
    def insert(self, table: str, record: dict[str, Any]) -> int:
        return self._table(table).insert(record)

    def bulk_insert(self, table: str, records: list[dict[str, Any]]) -> list[int]:
        return self._table(table).insert_multiple(records)

    def find(
        self, table: str, predicate: Callable[[dict[str, Any]], bool]
    ) -> list[dict[str, Any]]:
        return self._table(table).search(predicate)  # TinyDB accepts a lambda

    def get(self, table: str, **query_by) -> dict[str, Any] | None:
        "Return first record matching equality filters (or None)."
        Q = Query()
        expr = None
        for k, v in query_by.items():
            expr = (Q[k] == v) if expr is None else (expr & (Q[k] == v))
        return self._table(table).get(expr)

    def upsert(self, table: str, record: dict[str, Any], keys: list[str]):
        "Insert or update based on a composite key list."
        Q = Query()
        expr = None
        for k in keys:
            expr = (Q[k] == record[k]) if expr is None else (expr & (Q[k] == record[k]))
        self._table(table).upsert(record, expr)

    def all(self, table: str) -> list[dict[str, Any]]:
        return self._table(table).all()

    def clear(self, table: str):
        self._table(table).truncate()

    def drop(self, table: str):
        self._db.drop_table(table)

    # ---------- housekeeping ---------- #
    def close(self):
        self._db.close()


# singleton instance that other modules can import
doc_db = _DocDB()
