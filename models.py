"""Data models used across the app."""
from dataclasses import dataclass


@dataclass
class ShipmentRecord:
    shipment_id: str
    retailer: str
    invoice_amount: float
    deduction_amount: float
    deduction_reason: str
    appointment_time: str
    arrival_time: str
    delivered_in_full: bool
    cases_expected: int
    cases_received: int
    asn_submitted: bool
    label_compliant: bool
    dock_delay_hours: float
    carrier_name: str
    warehouse: str
    dispute_status: str
    owner: str
    dispute_deadline: str
    has_pod: bool
    has_bol: bool
    has_asn_log: bool
    has_gps: bool
    has_images: bool


@dataclass
class EvaluationResult:
    shipment_id: str
    valid_deduction: bool
    recoverable_amount: float
    confidence: str
    root_cause: str
    action: str
    explanation: str
    retailer_notes: str = ""
