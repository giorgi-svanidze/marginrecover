"""Business logic for deduction evaluation."""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from config import RETAILER_RULES
from models import EvaluationResult, ShipmentRecord


def compute_evidence_score(row: pd.Series) -> float:
    checks = [row["has_pod"], row["has_bol"], row["has_asn_log"], row["has_gps"], row["has_images"]]
    return sum(bool(x) for x in checks) / len(checks)


def evaluate_deduction(record: ShipmentRecord) -> EvaluationResult:
    appointment = pd.to_datetime(record.appointment_time)
    arrival = pd.to_datetime(record.arrival_time)
    on_time = arrival <= appointment
    reason = record.deduction_reason.lower().strip()
    rules = RETAILER_RULES.get(record.retailer, {})
    retailer_notes = rules.get("notes", "Standard terms apply.")

    valid = True
    recoverable = 0.0
    confidence = "Medium"
    root_cause = "Unclassified"
    action = "Review manually"
    explanation = "The rule engine could not classify this deduction with high confidence."

    if "late" in reason or "otif" in reason:
        if on_time and record.dock_delay_hours >= 2:
            valid = False
            recoverable = record.deduction_amount
            confidence = "High"
            root_cause = "Retailer dock congestion"
            action = "Dispute with POD, appointment confirmation, and geofence/ELD logs"
            explanation = (
                f"Carrier arrived on or before the appointment time, but unloading delay was "
                f"{record.dock_delay_hours:.1f} hours at the retailer dock."
            )
        elif not on_time:
            valid = True
            confidence = "High"
            root_cause = "Carrier late arrival"
            action = "Escalate to carrier management and review appointment planning"
            explanation = "Carrier arrival occurred after the scheduled appointment time."
        else:
            valid = False
            recoverable = record.deduction_amount
            confidence = "Medium"
            root_cause = "Potential retailer receiving issue"
            action = "Dispute with proof of on-time arrival"
            explanation = "Shipment appears on time with no clear supplier-side failure."

    elif "in-full" in reason or "short" in reason or "quantity" in reason:
        if record.delivered_in_full and record.cases_expected == record.cases_received:
            valid = False
            recoverable = record.deduction_amount
            confidence = "High"
            root_cause = "Retailer receiving discrepancy"
            action = "Dispute with BOL, POD, and warehouse pick confirmation"
            explanation = "Supplier records indicate full quantity shipped and received."
        else:
            valid = True
            confidence = "High"
            root_cause = "Supplier fulfillment miss"
            action = "Investigate pick accuracy and inventory allocation"
            explanation = f"Expected {record.cases_expected} cases, received {record.cases_received}."

    elif "asn" in reason or "edi" in reason:
        if record.asn_submitted:
            valid = False
            recoverable = record.deduction_amount
            confidence = "High"
            root_cause = "Retailer portal / EDI mismatch"
            action = "Dispute with ASN transmission log and acknowledgment receipt"
            explanation = "ASN appears to have been submitted successfully in supplier records."
        else:
            valid = True
            confidence = "High"
            root_cause = "Supplier EDI compliance miss"
            action = "Fix ASN workflow and add pre-shipment validation"
            explanation = "ASN was not submitted according to available records."

    elif "label" in reason or "barcode" in reason:
        if record.label_compliant:
            valid = False
            recoverable = record.deduction_amount
            confidence = "Medium"
            root_cause = "Retailer inspection discrepancy"
            action = "Dispute with pallet images and QA documentation"
            explanation = "Internal records indicate labeling was compliant."
        else:
            valid = True
            confidence = "High"
            root_cause = "Warehouse labeling error"
            action = f"Retrain warehouse staff and enforce {rules.get('label_standard', 'GS1-128')} compliance"
            explanation = "Labeling issue appears supported by supplier-side data."

    return EvaluationResult(
        shipment_id=record.shipment_id,
        valid_deduction=valid,
        recoverable_amount=recoverable,
        confidence=confidence,
        root_cause=root_cause,
        action=action,
        explanation=explanation,
        retailer_notes=retailer_notes,
    )


def evaluate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_fields = list(ShipmentRecord.__dataclass_fields__.keys())
    results = []
    for _, row in df.iterrows():
        record = ShipmentRecord(**{k: row[k] for k in required_fields})
        evaluation = evaluate_deduction(record)
        merged = row.to_dict()
        merged.update(asdict(evaluation))
        results.append(merged)
    evaluated = pd.DataFrame(results)
    evaluated["evidence_score"] = evaluated.apply(compute_evidence_score, axis=1)
    evaluated["priority_score"] = (
        evaluated["recoverable_amount"]
        * evaluated["evidence_score"]
        * evaluated["confidence"].map({"High": 1.0, "Medium": 0.7}).fillna(0.5)
    )
    return evaluated
