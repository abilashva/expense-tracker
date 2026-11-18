from decimal import Decimal

import pytest

from expense_tracker.storage import ExpenseStorage


@pytest.fixture
def storage():
    s = ExpenseStorage(":memory:")
    yield s
    s.close()


def test_add_and_list(storage):
    storage.add(Decimal("12.50"), "Food", "lunch", "2026-11-01")
    items = storage.list()
    assert len(items) == 1
    assert items[0].amount == Decimal("12.50")
    assert items[0].category == "food"  # normalised to lowercase


def test_filter_by_month_and_category(storage):
    storage.add(Decimal("10"), "food", "", "2026-10-15")
    storage.add(Decimal("20"), "food", "", "2026-11-02")
    storage.add(Decimal("30"), "travel", "", "2026-11-03")
    assert len(storage.list(month="2026-11")) == 2
    assert len(storage.list(month="2026-11", category="food")) == 1


def test_totals_by_category(storage):
    storage.add(Decimal("10.10"), "food", "", "2026-11-01")
    storage.add(Decimal("5.20"), "food", "", "2026-11-02")
    storage.add(Decimal("99.99"), "rent", "", "2026-11-01")
    assert storage.totals_by_category() == [
        ("rent", Decimal("99.99")),
        ("food", Decimal("15.30")),
    ]


def test_delete(storage):
    e = storage.add(Decimal("5"), "misc", "", "2026-11-01")
    assert storage.delete(e.id) is True
    assert storage.delete(e.id) is False
    assert storage.list() == []
