"""Offline monthly totals for an explicit, synthetic expense CSV contract.

This file can also be distributed unchanged as a zipapp's __main__.py.
It implements no official school, banking, NEIS or ERP import format.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import date
from decimal import Decimal, localcontext
from pathlib import Path


class ExpenseCsvError(ValueError):
    """A sanitized expense-file error that contains no input values."""


class ExpenseArguments(argparse.ArgumentParser):
    def error(self, message):
        raise ExpenseCsvError("invalid arguments; use --input and --output")


def convert_expense_csv(input_path: Path, output_path: Path) -> dict:
    """Validate every row, then exclusively publish sorted monthly totals.

    Existing outputs, including dangling symlinks, are never replaced. A
    private temporary output in the selected directory is removed on failure.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    try:
        same_path = input_path.resolve() == output_path.resolve()
    except (OSError, RuntimeError, ValueError):
        raise ExpenseCsvError("invalid input/output path") from None
    if same_path:
        raise ExpenseCsvError("input and output must use different paths")
    try:
        source_bytes = input_path.read_bytes()
        source_text = source_bytes.decode("utf-8-sig")
    except (OSError, UnicodeError):
        raise ExpenseCsvError("input cannot be read as UTF-8 CSV") from None

    groups: dict[tuple[str, str], tuple[int, int]] = {}
    row_count = 0
    reader = csv.reader(io.StringIO(source_text, newline=""), strict=True)
    try:
        if next(reader, None) != ["일자", "항목", "금액"]:
            raise ExpenseCsvError("row 1: expected headers 일자,항목,금액")
        for row_number, row in enumerate(reader, start=2):
            if len(row) != 3:
                raise ExpenseCsvError(f"row {row_number}: expected exactly three fields")
            day, category, amount = row
            if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day) is None:
                raise ExpenseCsvError(f"row {row_number}: invalid 일자")
            try:
                date.fromisoformat(day)
            except ValueError:
                raise ExpenseCsvError(f"row {row_number}: invalid 일자") from None
            if (
                not category.strip()
                or category.lstrip().startswith(("=", "+", "-", "@"))
                or any(
                    unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"}
                    for char in category
                )
            ):
                raise ExpenseCsvError(f"row {row_number}: invalid 항목")
            if re.fullmatch(r"[+-]?[0-9]{1,12}(?:\.[0-9]{1,2})?", amount) is None:
                raise ExpenseCsvError(f"row {row_number}: invalid 금액")
            with localcontext() as decimal_context:
                decimal_context.prec = 28
                cents = int(Decimal(amount) * 100)
            key = (day[:7], category)
            count, total_cents = groups.get(key, (0, 0))
            groups[key] = count + 1, total_cents + cents
            row_count += 1
    except csv.Error:
        raise ExpenseCsvError(f"row {reader.line_num}: invalid CSV fields") from None
    if row_count == 0:
        raise ExpenseCsvError("input has no expense rows")

    rendered = io.StringIO(newline="")
    writer = csv.writer(rendered)
    writer.writerow(["월", "항목", "건수", "합계"])
    for (month, category), (count, total_cents) in sorted(groups.items()):
        sign = "-" if total_cents < 0 else ""
        absolute_cents = abs(total_cents)
        total = f"{sign}{absolute_cents // 100}.{absolute_cents % 100:02}"
        writer.writerow([month, category, count, total])
    output_bytes = rendered.getvalue().encode("utf-8-sig")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output_path.parent, prefix=".monthly-expenses-", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(output_bytes)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.link(temporary_path, output_path)
    except FileExistsError:
        raise ExpenseCsvError("output already exists; select a new output") from None
    except OSError:
        raise ExpenseCsvError("output cannot be created") from None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return {
        "input_rows": row_count,
        "output_groups": len(groups),
        "input_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
    }


def run_expense_cli(argv=None) -> int:
    """Run standalone conversion, emitting only counts and file fingerprints."""
    parser = ExpenseArguments(
        prog="monthly-expenses",
        description="Aggregate a local expense CSV under the documented synthetic contract.",
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        result = convert_expense_csv(args.input, args.output)
    except ExpenseCsvError as error:
        print(f"expense CSV error: {error}", file=sys.stderr)
        return 2
    except SystemExit as error:
        return int(error.code)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_expense_cli())
