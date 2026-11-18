import csv

import pytest

from expense_tracker.cli import main


def run(tmp_path, *args):
    return main(["--db", str(tmp_path / "test.db"), *args])


def test_add_list_summary(tmp_path, capsys):
    assert run(tmp_path, "add", "12.50", "food", "-d", "lunch", "--date", "2026-11-01") == 0
    assert run(tmp_path, "list") == 0
    assert "lunch" in capsys.readouterr().out
    assert run(tmp_path, "summary") == 0
    assert "12.50" in capsys.readouterr().out


def test_delete_missing_returns_error(tmp_path):
    assert run(tmp_path, "delete", "42") == 1


def test_invalid_amount_rejected(tmp_path):
    with pytest.raises(SystemExit):
        run(tmp_path, "add", "-5", "food")


def test_export_csv(tmp_path):
    run(tmp_path, "add", "3.00", "coffee", "--date", "2026-11-01")
    out = tmp_path / "out.csv"
    assert run(tmp_path, "export", str(out)) == 0
    rows = list(csv.reader(out.open()))
    assert rows[0] == ["id", "date", "category", "amount", "description"]
    assert rows[1][2:4] == ["coffee", "3.00"]
