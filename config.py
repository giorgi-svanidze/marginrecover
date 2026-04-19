"""Configuration constants for MarginRecover."""

RETAILER_RULES = {
    "Walmart": {
        "otif_penalty": 0.03,
        "otif_threshold": 0.98,
        "asn_window_hrs": 2,
        "label_standard": "GS1-128",
        "dispute_window_days": 30,
        "notes": (
            "3% COGS penalty for OTIF below 98%. Geofence data and dock appointment "
            "confirmation are commonly used in disputes."
        ),
    },
    "Target": {
        "otif_penalty": 0.02,
        "otif_threshold": 0.95,
        "asn_window_hrs": 1,
        "label_standard": "UPC-A",
        "dispute_window_days": 45,
        "notes": "2% invoice penalty. POD and appointment confirmation are commonly required.",
    },
    "Amazon": {
        "otif_penalty": 0.05,
        "otif_threshold": 0.99,
        "asn_window_hrs": 0.5,
        "label_standard": "FNSKU",
        "dispute_window_days": 30,
        "notes": (
            "Strict compliance environment. Carrier GPS and timing evidence are critical "
            "for disputes."
        ),
    },
    "Kroger": {
        "otif_penalty": 0.015,
        "otif_threshold": 0.95,
        "asn_window_hrs": 4,
        "label_standard": "UPC-A",
        "dispute_window_days": 60,
        "notes": "More flexible ASN timing and longer dispute window than most large retailers.",
    },
    "Costco": {
        "otif_penalty": 0.02,
        "otif_threshold": 0.97,
        "asn_window_hrs": 2,
        "label_standard": "ITF-14",
        "dispute_window_days": 60,
        "notes": "Pallet-level label compliance is especially important.",
    },
}

INDUSTRY_BENCHMARKS = {
    "Deduction rate (% of revenue)": {"industry_avg": 2.1, "best_in_class": 1.0, "unit": "%", "lower_is_better": True},
    "Invalid deduction rate": {"industry_avg": 42, "best_in_class": 55, "unit": "%", "lower_is_better": False},
    "Recovery success rate (assumed)": {"industry_avg": 58, "best_in_class": 75, "unit": "%", "lower_is_better": False},
    "Avg resolution time (assumed days)": {"industry_avg": 45, "best_in_class": 21, "unit": " days", "lower_is_better": True},
}
