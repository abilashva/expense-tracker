from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Expense:
    """A single expense record."""

    id: int
    amount: Decimal
    category: str
    description: str
    date: str  # ISO format: YYYY-MM-DD
