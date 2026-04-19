"""Chart builders for the dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=trend_df["month"], y=trend_df["total_deductions"], name="Total deductions")
    fig.add_bar(x=trend_df["month"], y=trend_df["recoverable"], name="Recoverable")
    fig.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0))
    return fig


def root_cause_chart(results_df: pd.DataFrame) -> go.Figure:
    rc = results_df.groupby("root_cause", as_index=False).agg(
        total=("deduction_amount", "sum"),
        recoverable=("recoverable_amount", "sum"),
    ).sort_values("total", ascending=True)
    fig = go.Figure()
    fig.add_bar(y=rc["root_cause"], x=rc["total"], orientation="h", name="Total")
    fig.add_bar(y=rc["root_cause"], x=rc["recoverable"], orientation="h", name="Recoverable")
    fig.update_layout(barmode="overlay", height=300, margin=dict(l=0, r=0, t=10, b=0))
    return fig


def retailer_opportunity_chart(results_df: pd.DataFrame) -> go.Figure:
    by_retailer = results_df.groupby("retailer", as_index=False).agg(
        deductions=("deduction_amount", "sum"),
        recoverable=("recoverable_amount", "sum"),
    )
    return px.bar(
        by_retailer.sort_values("recoverable", ascending=False),
        x="retailer",
        y=["deductions", "recoverable"],
        barmode="group",
        height=280,
    )


def status_mix_chart(results_df: pd.DataFrame) -> go.Figure:
    status_df = results_df["dispute_status"].value_counts().rename_axis("status").reset_index(name="count")
    return px.pie(status_df, names="status", values="count", height=280)


def waterfall_chart(revenue: float, deduction_rate: float, invalid_pct: int, recovery_rate: int, preventable_pct: int) -> tuple[go.Figure, dict]:
    total_d = revenue * deduction_rate / 100
    invalid_d = total_d * invalid_pct / 100
    recover_d = invalid_d * recovery_rate / 100
    prevent_d = total_d * preventable_pct / 100
    ebitda = recover_d + prevent_d
    fig = go.Figure(go.Waterfall(
        measure=["absolute", "relative", "relative", "total"],
        x=["Total deductions", "Recovery (disputes)", "Prevention (ops)", "Net EBITDA upside"],
        y=[total_d, recover_d, prevent_d, 0],
        textposition="outside",
    ))
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=0))
    return fig, {
        "total_d": total_d,
        "recover_d": recover_d,
        "prevent_d": prevent_d,
        "ebitda": ebitda,
    }


def benchmark_bar(metric_name: str, mine: float, industry_avg: float, best_in_class: float, unit: str) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=[mine], y=["Current"], orientation="h")
    fig.add_vline(x=industry_avg, line_dash="dash", annotation_text=f"avg {industry_avg}{unit}")
    fig.add_vline(x=best_in_class, line_dash="dot", annotation_text=f"best {best_in_class}{unit}")
    fig.update_layout(height=90, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    return fig
