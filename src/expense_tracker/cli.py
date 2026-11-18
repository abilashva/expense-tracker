from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import __version__
from .export import export_csv
from .storage import ExpenseStorage

DEFAULT_DB = Path(os.environ.get("EXPENSE_DB", "~/.expense_tracker/expenses.db"))


def _amount(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"invalid amount: {value!r}")
    if amount <= 0 or amount != amount.quantize(Decimal("0.01")):
        raise argparse.ArgumentTypeError("amount must be positive with at most 2 decimals")
    return amount


def _date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError("date must be in YYYY-MM-DD format")


def _month(value: str) -> str:
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise argparse.ArgumentTypeError("month must be in YYYY-MM format")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expense", description="Track your expenses.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--db", default=DEFAULT_DB, help="path to the SQLite database")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add an expense")
    add.add_argument("amount", type=_amount)
    add.add_argument("category")
    add.add_argument("-d", "--description", default="")
    add.add_argument("--date", type=_date, default=date.today().isoformat())

    ls = sub.add_parser("list", help="list expenses")
    ls.add_argument("-m", "--month", type=_month)
    ls.add_argument("-c", "--category")

    rm = sub.add_parser("delete", help="delete an expense by id")
    rm.add_argument("id", type=int)

    summary = sub.add_parser("summary", help="show totals by category")
    summary.add_argument("-m", "--month", type=_month)

    exp = sub.add_parser("export", help="export expenses to CSV")
    exp.add_argument("path")
    exp.add_argument("-m", "--month", type=_month)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    storage = ExpenseStorage(args.db)
    try:
        if args.command == "add":
            e = storage.add(args.amount, args.category, args.description, args.date)
            print(f"Added #{e.id}: {e.amount:.2f} on {e.category} ({e.date})")

        elif args.command == "list":
            expenses = storage.list(args.month, args.category)
            if not expenses:
                print("No expenses found.")
            for e in expenses:
                print(f"#{e.id:<4} {e.date}  {e.category:<14} {e.amount:>10.2f}  {e.description}")

        elif args.command == "delete":
            if storage.delete(args.id):
                print(f"Deleted #{args.id}")
            else:
                print(f"No expense with id {args.id}", file=sys.stderr)
                return 1

        elif args.command == "summary":
            totals = storage.totals_by_category(args.month)
            if not totals:
                print("No expenses found.")
            for category, total in totals:
                print(f"{category:<14} {total:>10.2f}")
            if totals:
                print("-" * 25)
                print(f"{'TOTAL':<14} {sum(t for _, t in totals):>10.2f}")

        elif args.command == "export":
            count = export_csv(storage.list(args.month), args.path)
            print(f"Exported {count} expenses to {args.path}")
    finally:
        storage.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
