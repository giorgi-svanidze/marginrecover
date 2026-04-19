"""AI utilities with safe fallbacks."""
from __future__ import annotations

import textwrap

from config import RETAILER_RULES


def generate_fallback_dispute_letter(row: dict) -> str:
    return f"""Subject: Dispute of Deduction for Shipment {row['shipment_id']}

To Whom It May Concern,

We are formally disputing the deduction of ${row['deduction_amount']:,.0f} associated with shipment {row['shipment_id']} to {row['retailer']}.

Our internal review indicates that this deduction appears invalid for the following reason:
- Root cause assessment: {row['root_cause']}
- Explanation: {row['explanation']}

Supporting documentation recommended for this dispute includes:
- Proof of Delivery (POD)
- Bill of Lading (BOL)
- Appointment confirmation
- ASN transmission logs where applicable
- Carrier timing or GPS records where applicable

We respectfully request review and reimbursement of the deducted amount within 10 business days.

Sincerely,
Supply Chain Compliance Team
"""


def generate_dispute_letter(row: dict, api_key: str) -> str:
    if not api_key:
        return generate_fallback_dispute_letter(row)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        rules = RETAILER_RULES.get(row.get("retailer", ""), {})
        prompt = f"""You are a supply chain compliance expert writing a formal retailer chargeback dispute letter.

Shipment ID: {row['shipment_id']}
Retailer: {row['retailer']}
Invoice amount: ${row['invoice_amount']:,.0f}
Disputed deduction: ${row['deduction_amount']:,.0f}
Deduction reason: {row['deduction_reason']}
Appointment time: {row['appointment_time']}
Arrival time: {row['arrival_time']}
Delivered in full: {row['delivered_in_full']}
Cases expected / received: {row['cases_expected']} / {row['cases_received']}
ASN submitted: {row['asn_submitted']}
Label compliant: {row['label_compliant']}
Dock delay hours: {row['dock_delay_hours']}
Carrier: {row['carrier_name']}
Warehouse: {row['warehouse']}

Root cause: {row['root_cause']}
Explanation: {row['explanation']}
Retailer policy note: {rules.get('notes', 'Standard terms apply.')}

Write a professional dispute letter that:
1. clearly states the disputed amount
2. explains why the deduction appears invalid
3. uses concise bullet points for evidence
4. requests reimbursement within 10 business days
5. stays under 300 words
"""
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception:
        return generate_fallback_dispute_letter(row)


def generate_fallback_executive_summary(results_df, metrics: dict, root_causes: dict, retailers: dict) -> str:
    return (
        f"Current deductions total ${metrics['total_deductions']:,.0f}, with "
        f"${metrics['total_recoverable']:,.0f} appearing recoverable. Approximately "
        f"{metrics['invalid_rate']:.1f}% of deductions appear invalid based on the current rule set. "
        f"The largest loss drivers are concentrated in {', '.join(list(root_causes)[:2])}, "
        f"with retailer exposure highest in {', '.join(list(retailers)[:2])}. "
        f"Teams should prioritize high-value disputes with strong evidence readiness first."
    )


def generate_executive_summary(results_df, metrics: dict, root_causes: dict, retailers: dict, api_key: str) -> str:
    if not api_key:
        return generate_fallback_executive_summary(results_df, metrics, root_causes, retailers)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Write a concise executive summary for a supply chain revenue recovery dashboard.

Total deductions: {metrics['total_deductions']}
Recoverable revenue: {metrics['total_recoverable']}
Invalid deduction rate: {metrics['invalid_rate']}

Top root causes: {root_causes}
Retailer concentration: {retailers}

Write 4 short sentences that:
- identify the largest risks
- explain the recovery opportunity
- highlight where operations should focus
- sound executive and business-oriented
"""
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception:
        return generate_fallback_executive_summary(results_df, metrics, root_causes, retailers)
