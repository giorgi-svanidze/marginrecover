# MarginRecover

MarginRecover is an AI-assisted revenue recovery platform that helps suppliers detect invalid retailer chargebacks, prioritize disputes, assess evidence readiness, and quantify EBITDA upside from recovery and prevention.

## Demo

![Dashboard](images/dashboard.png)
![Dispute Queue](images/disputes.png)
![AI Letter](images/letter.png)

## What it does

Retailer OTIF and compliance deductions often leak revenue because finance sees the short pay, operations sees the shipping issue, and nobody has a fast dispute workflow. MarginRecover closes that gap by combining:

- rules-based deduction validation
- evidence-readiness scoring
- dispute prioritization
- AI-generated executive summaries
- AI-generated dispute letters
- impact simulation for finance and operations leaders

## Repo structure

```text
marginrecover_refactor/
├── app.py
├── ai.py
├── charts.py
├── components.py
├── config.py
├── data.py
├── metrics.py
├── models.py
├── rules.py
├── requirements.txt
└── sample_data.csv
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional AI setup

If you want live AI summaries and dispute letters, set an Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your_key_here"
```

Without an API key, the app still works using safe fallback text.
