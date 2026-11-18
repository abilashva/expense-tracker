from __future__ import annotations

import csv
from pathlib import Path

from .models import Expense


def export_csv(expenses: list[Expense], path: str | Path) -> int:
    """Write expenses to a CSV file and return the number of rows written."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "category", "amount", "description"])
        for e in expenses:
            writer.writerow([e.id, e.date, e.category, f"{e.amount:.2f}", e.description])
    return len(expenses)
