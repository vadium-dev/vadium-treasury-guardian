#!/usr/bin/env python3
"""Poll Circle CLI for an agent wallet's activity and flag spend anomalies.

MVP for the "Arc Treasury Guardian" spend-analytics wedge (see
docs/IDEA.md). Reads wallet operations Circle CLI already exposes — no new
integration required. Requires `circle` on PATH and an authenticated
session (`circle wallet login`).

Usage:
    python scripts/poll_spend.py --address 0xABC... --chain ARC --db spend.db
"""

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    tx_id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    chain TEXT NOT NULL,
    tx_type TEXT,          -- inbound / outbound
    operation TEXT,        -- transfer / execute
    state TEXT,
    counterparty TEXT,
    amount REAL,
    token TEXT,
    occurred_at TEXT
);

CREATE TABLE IF NOT EXISTS budget_snapshots (
    address TEXT NOT NULL,
    chain TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    daily_limit REAL,
    daily_remaining REAL,
    weekly_limit REAL,
    weekly_remaining REAL,
    monthly_limit REAL,
    monthly_remaining REAL,
    PRIMARY KEY (address, chain, captured_at)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

# Thresholds are deliberately simple for the MVP — tune once real spend
# patterns from a design partner are available.
SPIKE_MULTIPLIER = 3.0
NEW_COUNTERPARTY_ALERT_AMOUNT = 5.0  # USDC
BUDGET_LOW_FRACTION = 0.10


def run_circle(*args: str) -> dict | list:
    """Run a `circle` CLI subcommand with JSON output and return its `data` payload.

    Every `circle ... --output json` call wraps its payload as {"data": ...}
    on success or {"error": {...}} on failure (which we already catch via
    the non-zero exit code below).
    """
    cmd = ["circle", *args, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"circle {' '.join(args)} failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    return payload.get("data", payload) if isinstance(payload, dict) else payload


def ingest_transactions(conn: sqlite3.Connection, address: str, chain: str, limit: int = 50) -> None:
    data = run_circle("transaction", "list", "--address", address, "--chain", chain, "--limit", str(limit))
    rows = data.get("transactions", []) if isinstance(data, dict) else data
    for tx in rows:
        tx_type = (tx.get("transactionType") or "").lower()
        counterparty = tx.get("sourceAddress") if tx_type == "inbound" else tx.get("destinationAddress")
        amounts = tx.get("amounts") or []
        conn.execute(
            """INSERT OR IGNORE INTO transactions
               (tx_id, address, chain, tx_type, operation, state, counterparty, amount, token, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tx.get("id") or tx.get("txHash"),
                address,
                chain,
                tx_type,
                (tx.get("operation") or "").lower(),
                (tx.get("state") or "").lower(),
                counterparty,
                float(amounts[0]) if amounts else 0.0,
                "USDC",
                tx.get("createDate") or tx.get("firstConfirmDate"),
            ),
        )
    conn.commit()


def ingest_budget(conn: sqlite3.Connection, address: str, chain: str) -> None:
    """Spending-policy budgets are a mainnet-only feature (403 on testnet
    wallets) — skip quietly rather than failing the whole poll when
    unavailable.
    """
    try:
        budget = run_circle("wallet", "limit", "budget", "--address", address)
    except RuntimeError as exc:
        if "403" in str(exc) or "forbidden" in str(exc).lower():
            print("note: spending-policy budgets are mainnet-only; skipping on this wallet", file=sys.stderr)
            return
        raise
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO budget_snapshots
           (address, chain, captured_at, daily_limit, daily_remaining,
            weekly_limit, weekly_remaining, monthly_limit, monthly_remaining)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            address,
            chain,
            now,
            budget.get("dailyLimit"),
            budget.get("dailyRemaining"),
            budget.get("weeklyLimit"),
            budget.get("weeklyRemaining"),
            budget.get("monthlyLimit"),
            budget.get("monthlyRemaining"),
        ),
    )
    conn.commit()


def _raise_alert(conn: sqlite3.Connection, address: str, alert_type: str, severity: str, detail: str) -> None:
    conn.execute(
        "INSERT INTO alerts (address, alert_type, severity, detail, created_at) VALUES (?, ?, ?, ?, ?)",
        (address, alert_type, severity, detail, datetime.now(timezone.utc).isoformat()),
    )


def compute_alerts(conn: sqlite3.Connection, address: str) -> None:
    today = datetime.now(timezone.utc).date()
    window_start = (today - timedelta(days=7)).isoformat()

    todays_spend = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE address = ? AND tx_type = 'outbound' AND date(occurred_at) = ?",
        (address, today.isoformat()),
    ).fetchone()[0]

    rolling_avg = conn.execute(
        "SELECT COALESCE(AVG(daily_total), 0) FROM ("
        "  SELECT date(occurred_at) AS d, SUM(amount) AS daily_total FROM transactions"
        "  WHERE address = ? AND tx_type = 'outbound' AND occurred_at >= ? AND date(occurred_at) < ?"
        "  GROUP BY date(occurred_at)"
        ")",
        (address, window_start, today.isoformat()),
    ).fetchone()[0]

    if rolling_avg > 0 and todays_spend > rolling_avg * SPIKE_MULTIPLIER:
        _raise_alert(
            conn, address, "spend_spike", "high",
            f"Today's spend {todays_spend:.4f} USDC is {todays_spend / rolling_avg:.1f}x "
            f"the 7-day average of {rolling_avg:.4f} USDC",
        )

    new_counterparties = conn.execute(
        "SELECT counterparty, amount, occurred_at FROM transactions "
        "WHERE address = ? AND tx_type = 'outbound' AND amount >= ? AND date(occurred_at) = ? "
        "AND counterparty NOT IN ("
        "  SELECT DISTINCT counterparty FROM transactions "
        "  WHERE address = ? AND occurred_at < ?"
        ")",
        (address, NEW_COUNTERPARTY_ALERT_AMOUNT, today.isoformat(), address, window_start),
    ).fetchall()
    for counterparty, amount, occurred_at in new_counterparties:
        _raise_alert(
            conn, address, "new_high_value_counterparty", "medium",
            f"First-seen payment of {amount:.4f} USDC to {counterparty} at {occurred_at}",
        )

    latest_budget = conn.execute(
        "SELECT daily_limit, daily_remaining FROM budget_snapshots "
        "WHERE address = ? ORDER BY captured_at DESC LIMIT 1",
        (address,),
    ).fetchone()
    if latest_budget and latest_budget[0]:
        daily_limit, daily_remaining = latest_budget
        if daily_remaining is not None and daily_remaining < daily_limit * BUDGET_LOW_FRACTION:
            _raise_alert(
                conn, address, "budget_low", "medium",
                f"Daily budget remaining {daily_remaining:.4f} of {daily_limit:.4f} USDC "
                f"({daily_remaining / daily_limit:.0%})",
            )

    conn.commit()


def print_digest(conn: sqlite3.Connection, address: str) -> None:
    alerts = conn.execute(
        "SELECT alert_type, severity, detail, created_at FROM alerts "
        "WHERE address = ? ORDER BY created_at DESC LIMIT 20",
        (address,),
    ).fetchall()
    if not alerts:
        print(f"No alerts for {address}.")
        return
    print(f"Alerts for {address}:")
    for alert_type, severity, detail, created_at in alerts:
        print(f"  [{severity.upper()}] {alert_type}: {detail} ({created_at})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", required=True, help="Agent wallet address to monitor")
    parser.add_argument("--chain", default="ARC", help="Chain identifier (default: ARC)")
    parser.add_argument("--db", default="spend.db", help="SQLite file to store history/alerts in")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.executescript(SCHEMA)

    try:
        ingest_transactions(conn, args.address, args.chain)
        ingest_budget(conn, args.address, args.chain)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    compute_alerts(conn, args.address)
    print_digest(conn, args.address)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
