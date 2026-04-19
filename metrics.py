"""KPI and summarization helpers."""
from __future__ import annotations

import pandas as pd


def calculate_portfolio_metrics(results_df: pd.DataFrame) -> dict:
    total_deductions = float(results_df["deduction_amount"].sum())
    total_recoverable = float(results_df["recoverable_amount"].sum())
    total_invoice = float(results_df["invoice_amount"].sum())
    invalid_mask = results_df["valid_deduction"] == False
    leakage_rate = (total_deductions / total_invoice * 100) if total_invoice else 0.0
    invalid_rate = invalid_mask.mean() * 100 if len(results_df) else 0.0
    pending_mask = results_df["dispute_status"].isin(["New", "Under Review", "Submitted"])

    return {
        "total_deductions": total_deductions,
        "total_recoverable": total_recoverable,
        "total_invoice": total_invoice,
        "leakage_rate": leakage_rate,
        "invalid_rate": invalid_rate,
        "invalid_count": int(invalid_mask.sum()),
        "pending_count": int(pending_mask.sum()),
        "pending_open_value": float(results_df.loc[pending_mask, "recoverable_amount"].sum()),
        "won_count": int((results_df["dispute_status"] == "Won").sum()),
        "submitted_count": int((results_df["dispute_status"] == "Submitted").sum()),
        "won_recovery": float(results_df.loc[results_df["dispute_status"] == "Won", "deduction_amount"].sum()),
        "avg_evidence_readiness": float(results_df["evidence_score"].mean()) if len(results_df) else 0.0,
    }


def build_trend_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"month": "Oct", "total_deductions": 18200, "recoverable": 9100},
        {"month": "Nov", "total_deductions": 22400, "recoverable": 12300},
        {"month": "Dec", "total_deductions": 31500, "recoverable": 18200},
        {"month": "Jan", "total_deductions": 26800, "recoverable": 14500},
        {"month": "Feb", "total_deductions": 19600, "recoverable": 11200},
        {"month": "Mar", "total_deductions": 21200, "recoverable": 13400},
    ])


def top_root_causes(results_df: pd.DataFrame) -> dict:
    return (
        results_df.groupby("root_cause")["deduction_amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )


def retailer_concentration(results_df: pd.DataFrame) -> dict:
    return (
        results_df.groupby("retailer")["deduction_amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )
