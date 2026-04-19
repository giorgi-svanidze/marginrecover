"""Data loading, validation, and sample generation."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

import pandas as pd

from models import ShipmentRecord

REQUIRED_COLUMNS = list(ShipmentRecord.__dataclass_fields__.keys())


def get_sample_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"shipment_id":"SHP-1001","retailer":"Walmart","invoice_amount":100000,"deduction_amount":3000,"deduction_reason":"Late Delivery / OTIF","appointment_time":"2026-04-01 10:00","arrival_time":"2026-04-01 09:42","delivered_in_full":True,"cases_expected":1000,"cases_received":1000,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":6.0,"carrier_name":"Carrier X","warehouse":"Dallas DC","dispute_status":"New","owner":"Ops Team","dispute_deadline":"2026-05-01","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":True,"has_images":False},
        {"shipment_id":"SHP-1002","retailer":"Target","invoice_amount":85000,"deduction_amount":1800,"deduction_reason":"ASN Missing","appointment_time":"2026-04-03 09:00","arrival_time":"2026-04-03 08:55","delivered_in_full":True,"cases_expected":700,"cases_received":700,"asn_submitted":False,"label_compliant":True,"dock_delay_hours":1.0,"carrier_name":"Carrier Y","warehouse":"Chicago DC","dispute_status":"Lost","owner":"Compliance Team","dispute_deadline":"2026-05-18","has_pod":True,"has_bol":True,"has_asn_log":False,"has_gps":False,"has_images":False},
        {"shipment_id":"SHP-1003","retailer":"Amazon","invoice_amount":120000,"deduction_amount":4200,"deduction_reason":"In-Full Violation","appointment_time":"2026-04-05 12:00","arrival_time":"2026-04-05 11:35","delivered_in_full":True,"cases_expected":1500,"cases_received":1500,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":0.5,"carrier_name":"Carrier X","warehouse":"Atlanta DC","dispute_status":"Under Review","owner":"Recovery Analyst","dispute_deadline":"2026-05-05","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":False,"has_images":False},
        {"shipment_id":"SHP-1004","retailer":"Kroger","invoice_amount":76000,"deduction_amount":1200,"deduction_reason":"Label Non-Compliance","appointment_time":"2026-04-07 07:00","arrival_time":"2026-04-07 06:40","delivered_in_full":True,"cases_expected":600,"cases_received":600,"asn_submitted":True,"label_compliant":False,"dock_delay_hours":0.0,"carrier_name":"Carrier Z","warehouse":"Dallas DC","dispute_status":"Lost","owner":"Warehouse QA","dispute_deadline":"2026-06-06","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":False,"has_images":True},
        {"shipment_id":"SHP-1005","retailer":"Walmart","invoice_amount":92000,"deduction_amount":2760,"deduction_reason":"Late Delivery / OTIF","appointment_time":"2026-04-08 08:00","arrival_time":"2026-04-08 09:15","delivered_in_full":True,"cases_expected":900,"cases_received":900,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":0.5,"carrier_name":"Carrier Y","warehouse":"Dallas DC","dispute_status":"Lost","owner":"Carrier Manager","dispute_deadline":"2026-05-08","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":True,"has_images":False},
        {"shipment_id":"SHP-1006","retailer":"Amazon","invoice_amount":145000,"deduction_amount":7250,"deduction_reason":"Late Delivery / OTIF","appointment_time":"2026-04-09 06:00","arrival_time":"2026-04-09 05:50","delivered_in_full":True,"cases_expected":2000,"cases_received":2000,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":5.5,"carrier_name":"Carrier X","warehouse":"Atlanta DC","dispute_status":"Submitted","owner":"Recovery Analyst","dispute_deadline":"2026-05-09","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":True,"has_images":False},
        {"shipment_id":"SHP-1007","retailer":"Costco","invoice_amount":210000,"deduction_amount":3150,"deduction_reason":"In-Full Violation","appointment_time":"2026-04-10 09:00","arrival_time":"2026-04-10 08:45","delivered_in_full":False,"cases_expected":2500,"cases_received":2380,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":0.3,"carrier_name":"Carrier Z","warehouse":"LA DC","dispute_status":"Lost","owner":"Inventory Planner","dispute_deadline":"2026-06-09","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":False,"has_images":False},
        {"shipment_id":"SHP-1008","retailer":"Target","invoice_amount":67000,"deduction_amount":1340,"deduction_reason":"ASN Missing","appointment_time":"2026-04-11 10:00","arrival_time":"2026-04-11 09:55","delivered_in_full":True,"cases_expected":550,"cases_received":550,"asn_submitted":True,"label_compliant":True,"dock_delay_hours":0.2,"carrier_name":"Carrier Y","warehouse":"Chicago DC","dispute_status":"Won","owner":"Compliance Team","dispute_deadline":"2026-05-26","has_pod":True,"has_bol":True,"has_asn_log":True,"has_gps":False,"has_images":False},
    ])


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    numeric_cols = ["invoice_amount", "deduction_amount", "cases_expected", "cases_received", "dock_delay_hours"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    bool_cols = ["delivered_in_full", "asn_submitted", "label_compliant", "has_pod", "has_bol", "has_asn_log", "has_gps", "has_images"]
    for col in bool_cols:
        if out[col].dtype != bool:
            out[col] = out[col].astype(str).str.lower().map(
                {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
            )
    return out


def export_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def write_sample_csv(path: Path) -> None:
    get_sample_data().to_csv(path, index=False)
