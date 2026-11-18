# Expense Tracker

A small command-line expense tracker written in Python. Data is stored locally in SQLite, amounts are stored as integer cents (no floating-point errors), and there are no runtime dependencies.

## Features

- Add, list and delete expenses
- Filter by month (`YYYY-MM`) or category
- Totals per category
- Export to CSV
- Tested with `pytest`, CI via GitHub Actions

## Installation

```bash
git clone https://github.com/<your-username>/expense-tracker.git
cd expense-tracker
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

```bash
expense add 250.50 food -d "Team lunch"
expense add 1200 transport --date 2026-11-05
expense list
expense list -m 2026-11 -c food
expense summary -m 2026-11
expense export november.csv -m 2026-11
expense delete 3
```

The database lives at `~/.expense_tracker/expenses.db`. Override it with `--db PATH` or the `EXPENSE_DB` environment variable.

## Project structure

```
src/expense_tracker/
    cli.py       # argparse interface
    storage.py   # SQLite persistence
    models.py    # Expense dataclass
    export.py    # CSV export
tests/           # pytest suite
```

## Running tests

```bash
pytest
```

## Ideas for extension

- Monthly budgets with alerts
- Charts with matplotlib
- Recurring expenses
- Import from bank CSV statements

## License

MIT
