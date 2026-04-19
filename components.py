"""Reusable UI helpers."""
from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown("""
    <style>
        .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
        div[data-testid="metric-container"] { background: #111318; border: 1px solid #2a2f3d; border-radius: 10px; padding: 14px 16px; }
        div[data-testid="stSidebarContent"] { background: #0a0b0d; }
        .app-subtitle { color: #6b7280; font-size: 1rem; margin-top: -0.4rem; margin-bottom: 1.2rem; }
        .section-note { color: #6b7280; font-size: 0.92rem; }
        .status-new { color: #2563eb; font-weight: 600; }
        .status-review { color: #d97706; font-weight: 600; }
        .status-submitted { color: #7c3aed; font-weight: 600; }
        .status-won { color: #059669; font-weight: 600; }
        .status-lost { color: #dc2626; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)


def format_status(status: str) -> str:
    mapping = {
        "New": "status-new",
        "Under Review": "status-review",
        "Submitted": "status-submitted",
        "Won": "status-won",
        "Lost": "status-lost",
    }
    css_class = mapping.get(status, "status-new")
    return f"<span class='{css_class}'>{status}</span>"


def evidence_checklist(row: dict) -> None:
    cols = st.columns(5)
    labels = [
        ("POD", "has_pod"),
        ("BOL", "has_bol"),
        ("ASN Log", "has_asn_log"),
        ("GPS Data", "has_gps"),
        ("Images", "has_images"),
    ]
    for col, (label, key) in zip(cols, labels):
        col.write(f"{label}: {'✅' if row[key] else '❌'}")
    st.progress(float(row["evidence_score"]))
    st.caption(f"Evidence completeness: {row['evidence_score'] * 100:.0f}%")
