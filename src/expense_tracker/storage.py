from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

from .models import Expense

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    category     TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    date         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
"""


def _to_cents(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1")))


def _from_cents(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


class ExpenseStorage:
    """SQLite-backed persistence. Amounts are stored as integer cents."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        if str(db_path) != ":memory:":
            path = Path(db_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            db_path = str(path)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def add(self, amount: Decimal, category: str, description: str, date: str) -> Expense:
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO expenses (amount_cents, category, description, date) "
                "VALUES (?, ?, ?, ?)",
                (_to_cents(amount), category.lower(), description, date),
            )
        return Expense(cur.lastrowid, amount.quantize(Decimal("0.01")),
                       category.lower(), description, date)

    def list(self, month: str | None = None, category: str | None = None) -> list[Expense]:
        query, params = "SELECT * FROM expenses WHERE 1=1", []
        if month:
            query += " AND date LIKE ?"
            params.append(f"{month}-%")
        if category:
            query += " AND category = ?"
            params.append(category.lower())
        query += " ORDER BY date DESC, id DESC"
        return [self._row_to_expense(r) for r in self._conn.execute(query, params)]

    def delete(self, expense_id: int) -> bool:
        with self._conn:
            cur = self._conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        return cur.rowcount > 0

    def totals_by_category(self, month: str | None = None) -> list[tuple[str, Decimal]]:
        query, params = "SELECT category, SUM(amount_cents) AS total FROM expenses", []
        if month:
            query += " WHERE date LIKE ?"
            params.append(f"{month}-%")
        query += " GROUP BY category ORDER BY total DESC"
        return [(r["category"], _from_cents(r["total"]))
                for r in self._conn.execute(query, params)]

    @staticmethod
    def _row_to_expense(row: sqlite3.Row) -> Expense:
        return Expense(row["id"], _from_cents(row["amount_cents"]),
                       row["category"], row["description"], row["date"])
