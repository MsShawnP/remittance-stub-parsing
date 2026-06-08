"""SQLite ledger for remittance stub data.

Stores stubs, deductions, validation results, and reconciliation
outcomes. All financial amounts are stored as strings to preserve
exact Decimal precision — no floating-point drift.

Uses synchronous sqlite3 for simplicity. Async can be layered on
when FastAPI needs it.
"""

import json
import sqlite3
from decimal import Decimal
from pathlib import Path

from src.models import (
    ReconciliationMatch,
    ReconciliationResult,
    RemittanceStub,
    ValidationResult,
    ValidationStatus,
)


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS stubs (
    id TEXT PRIMARY KEY,
    retailer TEXT NOT NULL,
    check_number TEXT,
    payment_date TEXT,
    gross_invoice TEXT,
    net_cash TEXT,
    payer_name TEXT,
    source_file TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stub_id TEXT NOT NULL REFERENCES stubs(id),
    invoice_number TEXT,
    reason_code TEXT,
    reason_description TEXT,
    amount TEXT,
    deduction_date TEXT,
    category TEXT
);

CREATE TABLE IF NOT EXISTS validation_results (
    stub_id TEXT PRIMARY KEY REFERENCES stubs(id),
    status TEXT NOT NULL,
    arithmetic_valid INTEGER,
    all_codes_mapped INTEGER,
    discrepancy_amount TEXT,
    details_json TEXT
);

CREATE TABLE IF NOT EXISTS reconciliation_results (
    stub_id TEXT PRIMARY KEY REFERENCES stubs(id),
    match_status TEXT NOT NULL,
    matched_amount TEXT,
    unmatched_amount TEXT,
    dispute_window_days_remaining INTEGER,
    details_json TEXT
);
"""


def init_database(db_path: Path) -> sqlite3.Connection:
    """Create tables if they don't exist and enable WAL mode.

    Returns an open connection to the database.
    """
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    return conn


def insert_stub(conn: sqlite3.Connection, stub: RemittanceStub, stub_id: str) -> None:
    """Insert a stub and its deductions into the ledger.

    Uses a transaction so the stub and its deductions are atomic.
    """
    conn.execute(
        """
        INSERT OR REPLACE INTO stubs (id, retailer, check_number, payment_date,
                                      gross_invoice, net_cash, payer_name, source_file)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            stub_id,
            stub.retailer.value,
            stub.check_number,
            stub.payment_date.isoformat() if stub.payment_date else None,
            str(stub.gross_invoice),
            str(stub.net_cash),
            stub.payer_name,
            stub.source_file,
        ),
    )

    # Delete existing deductions for this stub (supports re-sync)
    conn.execute("DELETE FROM deductions WHERE stub_id = ?", (stub_id,))

    for deduction in stub.deductions:
        # Resolve category from reason code config if possible
        category = _resolve_category(deduction.reason_code, stub.retailer.value)

        conn.execute(
            """
            INSERT INTO deductions (stub_id, invoice_number, reason_code,
                                    reason_description, amount, deduction_date, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stub_id,
                deduction.invoice_number,
                deduction.reason_code,
                deduction.reason_description,
                str(deduction.amount),
                deduction.deduction_date.isoformat() if deduction.deduction_date else None,
                category,
            ),
        )

    conn.commit()


def _resolve_category(reason_code: str, retailer_value: str) -> str:
    """Look up the deduction category for a reason code.

    Returns "unknown" if the code isn't in the retailer's config.
    Catches errors silently — category is informational, not critical.
    """
    from src.models import RetailerFormat, load_reason_codes

    try:
        retailer = RetailerFormat(retailer_value)
        codes = load_reason_codes(retailer)
        if reason_code in codes:
            return codes[reason_code].category.value
    except (ValueError, FileNotFoundError):
        pass
    return "unknown"


def insert_validation_result(
    conn: sqlite3.Connection, result: ValidationResult
) -> None:
    """Insert or update a validation result for a stub."""
    details_json = json.dumps(
        [d.model_dump() for d in result.details]
    )

    conn.execute(
        """
        INSERT OR REPLACE INTO validation_results
            (stub_id, status, arithmetic_valid, all_codes_mapped,
             discrepancy_amount, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            result.stub_id,
            result.status.value,
            1 if result.arithmetic_valid else 0,
            1 if result.all_codes_mapped else 0,
            str(result.discrepancy_amount) if result.discrepancy_amount else None,
            details_json,
        ),
    )
    conn.commit()


def insert_reconciliation_result(
    conn: sqlite3.Connection, result: ReconciliationResult
) -> None:
    """Insert or update a reconciliation result for a stub."""
    details_json = json.dumps(result.details)

    conn.execute(
        """
        INSERT OR REPLACE INTO reconciliation_results
            (stub_id, match_status, matched_amount, unmatched_amount,
             dispute_window_days_remaining, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            result.stub_id,
            result.match_status.value,
            str(result.matched_amount),
            str(result.unmatched_amount),
            result.dispute_window_days_remaining,
            details_json,
        ),
    )
    conn.commit()


def get_all_stubs(conn: sqlite3.Connection) -> list[dict]:
    """Retrieve all stubs with their deductions.

    Returns a list of dicts, each containing stub fields and a
    nested 'deductions' list.
    """
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM stubs ORDER BY created_at")
    stubs = []

    for row in cursor:
        stub_dict = dict(row)

        # Fetch deductions for this stub
        ded_cursor = conn.execute(
            "SELECT * FROM deductions WHERE stub_id = ? ORDER BY id",
            (stub_dict["id"],),
        )
        stub_dict["deductions"] = [dict(d) for d in ded_cursor]
        stubs.append(stub_dict)

    conn.row_factory = None
    return stubs


def get_stub_summary(conn: sqlite3.Connection) -> dict:
    """Summary stats: total stubs, verified/flagged counts, total amounts.

    Returns a dict with keys: total_stubs, verified, flagged,
    total_gross, total_net, total_deductions.
    """
    # Total stub count
    total = conn.execute("SELECT COUNT(*) FROM stubs").fetchone()[0]

    # Validation counts
    verified = conn.execute(
        "SELECT COUNT(*) FROM validation_results WHERE status = 'verified'"
    ).fetchone()[0]
    flagged = conn.execute(
        "SELECT COUNT(*) FROM validation_results WHERE status = 'flagged'"
    ).fetchone()[0]

    # Financial totals — stored as strings, sum in Python for precision
    gross_rows = conn.execute("SELECT gross_invoice FROM stubs").fetchall()
    total_gross = sum(
        (Decimal(row[0]) for row in gross_rows if row[0]), start=Decimal("0")
    )

    net_rows = conn.execute("SELECT net_cash FROM stubs").fetchall()
    total_net = sum(
        (Decimal(row[0]) for row in net_rows if row[0]), start=Decimal("0")
    )

    ded_rows = conn.execute("SELECT amount FROM deductions").fetchall()
    total_deductions = sum(
        (Decimal(row[0]) for row in ded_rows if row[0]), start=Decimal("0")
    )

    return {
        "total_stubs": total,
        "verified": verified,
        "flagged": flagged,
        "total_gross": total_gross,
        "total_net": total_net,
        "total_deductions": total_deductions,
    }
