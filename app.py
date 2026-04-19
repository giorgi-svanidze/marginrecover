"""MarginRecover main Streamlit application."""
from __future__ import annotations

import os
import io

import pandas as pd
import streamlit as st

from ai import generate_dispute_letter, generate_executive_summary
from charts import (
    benchmark_bar,
    retailer_opportunity_chart,
    root_cause_chart,
    status_mix_chart,
    trend_chart,
    waterfall_chart,
)
from components import apply_styles, evidence_checklist, format_status
from config import INDUSTRY_BENCHMARKS, RETAILER_RULES
from data import export_csv_bytes, get_sample_data, normalize_types, validate_dataframe
from metrics import build_trend_data, calculate_portfolio_metrics, retailer_concentration, top_root_causes
from rules import evaluate_dataframe


st.set_page_config(
    page_title="MarginRecover",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()

with st.sidebar:
    st.markdown("## MarginRecover")
    st.caption("v4.0 · Revenue recovery platform")
    st.divider()

    api_key = st.text_input(
        "Anthropic API key",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Optional. Enables AI summaries and AI dispute letter drafting.",
    )
    if api_key:
        st.success("AI features enabled", icon="✅")
    else:
        st.info("AI features will use fallback text until an API key is added.")

    st.divider()
    st.subheader("Data Source")
    uploaded_file = st.file_uploader("Upload deductions CSV", type=["csv"])
    use_sample = st.checkbox("Use built-in sample data", value=True)
    st.divider()
    st.caption("Built for CPG/FMCG suppliers facing retailer OTIF and compliance deductions.")

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
elif use_sample:
    raw_df = get_sample_data()
else:
    st.info("Upload a CSV or enable sample data to begin.")
    st.stop()

is_valid, missing_cols = validate_dataframe(raw_df)
if not is_valid:
    st.error("Uploaded CSV is missing required columns.")
    st.code("\n".join(missing_cols))
    st.stop()

results_df = evaluate_dataframe(normalize_types(raw_df))
metrics = calculate_portfolio_metrics(results_df)
trend_df = build_trend_data()
root_causes = top_root_causes(results_df)
retailers = retailer_concentration(results_df)

st.title("MarginRecover")
st.markdown(
    "<div class='app-subtitle'>Identifies invalid retailer chargebacks, prioritizes dispute readiness, and models recoverable revenue across supply chain operations.</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Deduction Log",
    "Dispute Queue",
    "Impact Simulator",
    "Benchmarks",
])

with tab1:
    st.subheader("Portfolio Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recoverable Revenue", f"${metrics['total_recoverable']:,.0f}", f"{(metrics['total_recoverable'] / metrics['total_deductions'] * 100):.1f}% of deductions" if metrics["total_deductions"] else None)
    c2.metric("Total Deductions", f"${metrics['total_deductions']:,.0f}", f"{metrics['leakage_rate']:.2f}% revenue leakage")
    c3.metric("Invalid Deduction Rate", f"{metrics['invalid_rate']:.1f}%", f"{metrics['invalid_count']} of {len(results_df)} deductions")
    c4.metric("Pending Recovery Cases", f"{metrics['pending_count']}", f"${metrics['pending_open_value']:,.0f} open value")

    st.divider()
    st.subheader("AI Executive Summary")
    if "exec_summary" not in st.session_state:
        st.session_state["exec_summary"] = generate_executive_summary(results_df, metrics, root_causes, retailers, api_key)
    if st.button("Refresh Executive Summary"):
        st.session_state["exec_summary"] = generate_executive_summary(results_df, metrics, root_causes, retailers, api_key)
    st.info(st.session_state["exec_summary"])

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Won Cases", f"{metrics['won_count']}")
    p2.metric("Submitted Cases", f"{metrics['submitted_count']}")
    p3.metric("Recovered Value Won", f"${metrics['won_recovery']:,.0f}")
    p4.metric("Avg Evidence Readiness", f"{metrics['avg_evidence_readiness'] * 100:.0f}%")

    left, right = st.columns(2)
    left.markdown("**6-Month Deduction Trend**")
    left.plotly_chart(trend_chart(trend_df), use_container_width=True)
    right.markdown("**Root Cause Breakdown**")
    right.plotly_chart(root_cause_chart(results_df), use_container_width=True)

    c_left, c_right = st.columns(2)
    c_left.markdown("**Recovery Opportunity by Retailer**")
    c_left.plotly_chart(retailer_opportunity_chart(results_df), use_container_width=True)
    c_right.markdown("**Workflow Status Mix**")
    c_right.plotly_chart(status_mix_chart(results_df), use_container_width=True)

with tab2:
    st.subheader("Evaluated Deductions")
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        search = st.text_input("Search", placeholder="Shipment ID, retailer, reason…", label_visibility="collapsed")
    with fc2:
        retailer_filter = st.selectbox("Retailer", ["All"] + sorted(results_df["retailer"].unique().tolist()), label_visibility="collapsed")
    with fc3:
        status_filter = st.selectbox("Status", ["All", "Invalid (dispute)", "Valid"], label_visibility="collapsed")

    filtered = results_df.copy()
    if search:
        mask = (
            filtered["shipment_id"].astype(str).str.contains(search, case=False, na=False)
            | filtered["retailer"].astype(str).str.contains(search, case=False, na=False)
            | filtered["deduction_reason"].astype(str).str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if retailer_filter != "All":
        filtered = filtered[filtered["retailer"] == retailer_filter]
    if status_filter == "Invalid (dispute)":
        filtered = filtered[~filtered["valid_deduction"]]
    elif status_filter == "Valid":
        filtered = filtered[filtered["valid_deduction"]]

    display_cols = [
        "shipment_id", "retailer", "deduction_reason", "deduction_amount",
        "valid_deduction", "recoverable_amount", "root_cause", "confidence",
        "dispute_status", "evidence_score",
    ]
    display = filtered[display_cols].copy()
    display.columns = [
        "Shipment", "Retailer", "Reason", "Deduction", "Valid",
        "Recoverable", "Root Cause", "Confidence", "Workflow Status", "Evidence Readiness",
    ]
    display["Valid"] = display["Valid"].map({True: "Valid", False: "Dispute"})
    display["Deduction"] = display["Deduction"].apply(lambda x: f"${x:,.0f}")
    display["Recoverable"] = display["Recoverable"].apply(lambda x: f"${x:,.0f}" if x > 0 else "—")
    display["Evidence Readiness"] = display["Evidence Readiness"].apply(lambda x: f"{x*100:.0f}%")
    st.dataframe(display, use_container_width=True, height=360)

    st.download_button(
        "Export filtered results as CSV",
        data=export_csv_bytes(filtered),
        file_name="marginrecover_filtered_export.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Case Detail")
    if len(filtered) > 0:
        selected_id = st.selectbox("Select shipment to inspect", filtered["shipment_id"].tolist())
        row = filtered[filtered["shipment_id"] == selected_id].iloc[0].to_dict()
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Shipment Data**")
            st.write(f"**Shipment ID:** {row['shipment_id']}")
            st.write(f"**Retailer:** {row['retailer']}")
            st.write(f"**Invoice Amount:** ${float(row['invoice_amount']):,.0f}")
            st.write(f"**Deduction Amount:** ${float(row['deduction_amount']):,.0f}")
            st.write(f"**Deduction Reason:** {row['deduction_reason']}")
            st.write(f"**Appointment Time:** {row['appointment_time']}")
            st.write(f"**Arrival Time:** {row['arrival_time']}")
            st.write(f"**Dock Delay Hours:** {float(row['dock_delay_hours']):.1f}")
            st.write(f"**Carrier:** {row['carrier_name']}")
            st.write(f"**Warehouse:** {row['warehouse']}")
            st.write(f"**Owner:** {row['owner']}")
            st.write(f"**Dispute Deadline:** {row['dispute_deadline']}")
        with d2:
            st.markdown("**Decision**")
            st.write(f"**Valid Deduction:** {'Yes' if row['valid_deduction'] else 'No'}")
            st.write(f"**Recoverable Amount:** ${row['recoverable_amount']:,.0f}")
            st.write(f"**Root Cause:** {row['root_cause']}")
            st.write(f"**Confidence:** {row['confidence']}")
            st.write(f"**Recommended Action:** {row['action']}")
            st.write(f"**Workflow Status:** {row['dispute_status']}")
            st.write(f"**Evidence Readiness:** {row['evidence_score'] * 100:.0f}%")
            st.info(row["explanation"])
        st.markdown("**Evidence Checklist**")
        evidence_checklist(row)

with tab3:
    disputes = results_df[~results_df["valid_deduction"]].copy().sort_values("priority_score", ascending=False)
    st.subheader(f"Dispute Queue — {len(disputes)} open dispute candidates")
    for _, row_series in disputes.iterrows():
        row = row_series.to_dict()
        rules = RETAILER_RULES.get(row["retailer"], {})
        with st.expander(f"{row['shipment_id']} · {row['retailer']} · {row['deduction_reason']} · ${row['recoverable_amount']:,.0f} recoverable"):
            q1, q2 = st.columns([3, 2])
            with q1:
                st.markdown(f"**Root Cause:** {row['root_cause']}")
                st.markdown(f"**Explanation:** {row['explanation']}")
                st.markdown(f"**Recommended Action:** {row['action']}")
                st.markdown(f"**Priority Score:** {row['priority_score']:,.0f}")
            with q2:
                st.markdown(f"**Deduction:** ${row['deduction_amount']:,.0f}")
                st.markdown(f"**Invoice:** ${row['invoice_amount']:,.0f}")
                st.markdown(f"**Confidence:** {row['confidence']}")
                st.markdown(f"**Owner:** {row['owner']}")
                st.markdown(f"**Deadline:** {row['dispute_deadline']}")
                st.markdown("**Status:**")
                st.markdown(format_status(row["dispute_status"]), unsafe_allow_html=True)
                if rules:
                    st.markdown(f"**Retailer Dispute Window:** {rules.get('dispute_window_days', 30)} days")
            st.markdown("**Evidence Checklist**")
            evidence_checklist(row)

            new_status = st.selectbox(
                "Update Status",
                ["New", "Under Review", "Submitted", "Won", "Lost"],
                index=["New", "Under Review", "Submitted", "Won", "Lost"].index(row["dispute_status"]),
                key=f"status_{row['shipment_id']}",
            )
            st.caption(f"Selected status update: {new_status} (demo only — not yet persisted)")
            st.markdown(f"**Retailer Policy Note:** {row.get('retailer_notes', '')}")

            if st.button(f"Generate Dispute Letter for {row['shipment_id']}", key=f"letter_btn_{row['shipment_id']}"):
                st.session_state[f"letter_{row['shipment_id']}"] = generate_dispute_letter(row, api_key)
            if f"letter_{row['shipment_id']}" in st.session_state:
                letter_text = st.session_state[f"letter_{row['shipment_id']}"]
                st.text_area("Generated dispute letter", value=letter_text, height=260, key=f"letter_box_{row['shipment_id']}")
                st.download_button(
                    "Download letter (.txt)",
                    data=letter_text,
                    file_name=f"dispute_{row['shipment_id']}.txt",
                    mime="text/plain",
                    key=f"download_letter_{row['shipment_id']}",
                )

with tab4:
    st.subheader("EBITDA Impact Simulator")
    st.markdown("<div class='section-note'>Model annual deduction leakage, recoverable value, and preventable loss reduction at different revenue scales.</div>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        revenue = st.number_input("Annual Revenue ($)", value=500_000_000, step=10_000_000, format="%d")
        deduction_rate = st.slider("Deduction % of Revenue", 0.0, 10.0, 3.0, 0.1, format="%.1f%%")
        invalid_pct = st.slider("Invalid Deduction %", 0, 80, 50, 1, format="%d%%")
    with s2:
        recovery_rate = st.slider("Recovery Success Rate", 0, 90, 60, 1, format="%d%%")
        preventable_pct = st.slider("Preventable via Ops Fixes", 0, 70, 35, 1, format="%d%%")
    wf_fig, wf = waterfall_chart(revenue, deduction_rate, invalid_pct, recovery_rate, preventable_pct)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Deductions", f"${wf['total_d']:,.0f}")
    m2.metric("Recoverable", f"${wf['recover_d']:,.0f}")
    m3.metric("Preventable", f"${wf['prevent_d']:,.0f}")
    m4.metric("Total EBITDA Upside", f"${wf['ebitda']:,.0f}", f"{wf['ebitda'] / revenue * 100:.2f}% of revenue")
    st.plotly_chart(wf_fig, use_container_width=True)
    st.info(
        f"At ${revenue / 1e6:.0f}M revenue and a {deduction_rate:.1f}% deduction rate, a structured recovery program could unlock approximately ${wf['ebitda']:,.0f} in annual EBITDA upside."
    )

with tab5:
    st.subheader("Industry Benchmark Comparison")
    st.markdown("<div class='section-note'>Some values below are calculated from the current dataset, while others are placeholder assumptions for product demonstration.</div>", unsafe_allow_html=True)

    my_metrics = {
        "Deduction rate (% of revenue)": metrics["leakage_rate"],
        "Invalid deduction rate": metrics["invalid_rate"],
        "Recovery success rate (assumed)": 60.0,
        "Avg resolution time (assumed days)": 38.0,
    }
    for metric_name, bench in INDUSTRY_BENCHMARKS.items():
        b1, b2 = st.columns([3, 1])
        mine = my_metrics[metric_name]
        with b1:
            st.markdown(f"**{metric_name}**")
            st.plotly_chart(
                benchmark_bar(metric_name, mine, bench["industry_avg"], bench["best_in_class"], bench["unit"]),
                use_container_width=True,
            )
        with b2:
            st.metric("Current", f"{mine:.1f}{bench['unit']}")

    st.divider()
    st.subheader("Retailer OTIF Policy Reference")
    rules_df = pd.DataFrame([
        {
            "Retailer": retailer,
            "OTIF Penalty": f"{rule['otif_penalty'] * 100:.1f}%",
            "OTIF Threshold": f"{rule['otif_threshold'] * 100:.0f}%",
            "ASN Window": f"{int(rule['asn_window_hrs'] * 60)} min" if rule["asn_window_hrs"] < 1 else f"{rule['asn_window_hrs']:.0f} hr",
            "Label Standard": rule["label_standard"],
            "Dispute Window": f"{rule['dispute_window_days']} days",
        }
        for retailer, rule in RETAILER_RULES.items()
    ])
    st.dataframe(rules_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Future Enhancements")
    st.markdown(
        """
1. Persist case statuses and dispute outcomes to a database  
2. Add automated evidence packet assembly for disputes  
3. Ingest carrier and EDI data through APIs  
4. Score dispute success probability from historical outcomes  
5. Add role-based access and team dashboards  
"""
    )
