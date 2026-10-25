#!/usr/bin/env python3
"""
MSME AI Cash-Flow UPI Estimator — Starter
---------------------------------------
Reconciles sample UPI transactions with open invoices,
estimates short-term cash flow, and surfaces GST impact.

Designed as a practical, dependency-free foundation for
Indian MSME fintech tools.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

# ---------------------------------------------------------------------------
# Sample data generators (replace with real CSV/Excel loaders in production)
# ---------------------------------------------------------------------------

def generate_sample_invoices(n: int = 8) -> List[Dict]:
    """Create realistic open invoices for an MSME."""
    base_date = datetime(2026, 10, 10)
    invoices = []
    for i in range(n):
        amount = random.choice([12500, 18750, 24000, 31500, 42000, 56000, 78000])
        invoices.append({
            "invoice_id": f"INV-2026-{1000 + i}",
            "customer": f"Customer {chr(65 + i)}",
            "amount": amount,
            "due_date": base_date + timedelta(days=random.randint(2, 18)),
            "gst_rate": 0.18,          # 18% GST typical for many services/goods
            "description": f"Supply of goods/services - batch {i+1}"
        })
    return invoices


def generate_sample_upi_transactions(n: int = 10) -> List[Dict]:
    """Create sample UPI inflows (some will match invoices)."""
    base_date = datetime(2026, 10, 12)
    txns = []
    for i in range(n):
        amount = random.choice([12500, 18750, 24000, 31500, 42000, 9999, 15000])
        txns.append({
            "txn_id": f"UPI{random.randint(100000000, 999999999)}",
            "amount": amount,
            "date": base_date + timedelta(days=random.randint(0, 10)),
            "payer_vpa": f"user{i}@okhdfcbank",
            "reference": f"INV-2026-{1000 + random.randint(0, 7)}" if random.random() > 0.3 else ""
        })
    return txns


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def match_upi_to_invoices(txns: List[Dict], invoices: List[Dict],
                          amount_tolerance: float = 1.0,
                          date_window_days: int = 5) -> Dict:
    """
    Simple reconciliation:
    1. Exact or near-exact amount match
    2. Within a date window around invoice due date
    3. Optional reference string match
    """
    matched = []
    unmatched_txns = []
    unmatched_invoices = invoices.copy()

    for txn in txns:
        best_match: Optional[Dict] = None
        for inv in unmatched_invoices:
            amount_ok = abs(txn["amount"] - inv["amount"]) <= amount_tolerance
            date_ok = abs((txn["date"] - inv["due_date"]).days) <= date_window_days
            ref_ok = (not txn["reference"]) or (txn["reference"] in inv["invoice_id"])

            if amount_ok and date_ok and ref_ok:
                best_match = inv
                break

        if best_match:
            matched.append({"txn": txn, "invoice": best_match})
            unmatched_invoices.remove(best_match)
        else:
            unmatched_txns.append(txn)

    return {
        "matched": matched,
        "unmatched_txns": unmatched_txns,
        "unmatched_invoices": unmatched_invoices
    }


def estimate_cashflow(matched: List[Dict], days: int = 14) -> Dict:
    """Simple 14-day cash inflow estimate + working-capital suggestion."""
    today = datetime(2026, 10, 25)
    daily = {}
    total_reconciled = 0.0

    for pair in matched:
        txn_date = pair["txn"]["date"]
        if (txn_date - today).days <= days:
            key = txn_date.strftime("%Y-%m-%d")
            daily[key] = daily.get(key, 0) + pair["txn"]["amount"]
            total_reconciled += pair["txn"]["amount"]

    # Very simple moving-average style buffer (placeholder for real forecasting)
    avg_daily = total_reconciled / max(days, 1)
    suggested_buffer = avg_daily * 7   # one week of buffer

    return {
        "total_reconciled_inflows": total_reconciled,
        "daily_breakdown": daily,
        "suggested_working_capital_buffer": round(suggested_buffer, 2)
    }


def estimate_gst_impact(invoices: List[Dict]) -> float:
    """Rough GST cash outflow estimate on taxable invoices."""
    return round(sum(inv["amount"] * inv["gst_rate"] for inv in invoices), 2)


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("MSME AI Cash-Flow UPI Estimator — Demo Run")
    print("=" * 60)

    invoices = generate_sample_invoices()
    txns = generate_sample_upi_transactions()

    result = match_upi_to_invoices(txns, invoices)
    cashflow = estimate_cashflow(result["matched"])
    gst_outflow = estimate_gst_impact(invoices)

    print(f"\nMatched pairs: {len(result['matched'])}")
    for pair in result["matched"]:
        t = pair["txn"]
        inv = pair["invoice"]
        print(f"  {t['txn_id']}  ₹{t['amount']:,}  →  {inv['invoice_id']} ({inv['customer']})")

    print(f"\nUnmatched UPI transactions: {len(result['unmatched_txns'])}")
    print(f"Open invoices still unmatched: {len(result['unmatched_invoices'])}")

    print(f"\n14-day reconciled inflows: ₹{cashflow['total_reconciled_inflows']:,.0f}")
    print(f"Suggested working-capital buffer: ₹{cashflow['suggested_working_capital_buffer']:,.0f}")
    print(f"Estimated GST cash impact (on sample invoices): ₹{gst_outflow:,.0f}")

    print("\n" + "=" * 60)
    print("Next: replace sample generators with real UPI/invoice data.")
    print("=" * 60)


if __name__ == "__main__":
    main()
