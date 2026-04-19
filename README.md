# MarginRecover

> Recover lost revenue from retailer chargebacks using data validation and automated dispute generation.

MarginRecover is a supply chain analytics tool that helps suppliers identify invalid retailer chargebacks, prioritize disputes, and recover lost revenue through structured workflows and automation.

---

## 🚀 Core Capabilities

- Rule-based deduction validation  
- Evidence-readiness scoring  
- Dispute prioritization pipeline  
- Automated dispute letter generation  
- Revenue impact simulation  

---

## 📊 Demo

### Portfolio Dashboard — Revenue leakage visibility
<img src="images/dashboard.png" width="700"/>

### Dispute Queue — Prioritized recovery pipeline
<img src="images/disputes.png" width="700"/>

### AI Dispute Letter — Automated claim documentation
<img src="images/letter.png" width="700"/>

---

## 🧩 Tech Stack

- Python  
- Streamlit (frontend UI)  
- Pandas (data processing)  
- Rule-based validation engine  
- Modular architecture (data, rules, metrics, AI layers)  

---

## ⚙️ What it does

Retailer OTIF and compliance deductions often leak revenue because:

- finance sees the short pay  
- operations sees the shipment  
- no one owns dispute execution  

MarginRecover closes this gap by combining:

- structured validation logic  
- automated documentation  
- decision support for recovery  

---

## 🛠 Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
---

## 🤖 Optional AI setup

If you want live AI summaries and dispute letters, set an API key:

export ANTHROPIC_API_KEY="your_key_here"

Without an API key, the app still works using fallback logic.

---

## 📁 Repo structure

marginrecover/  
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
├── sample_data.csv  
└── images/  
  ├── dashboard.png  
  ├── disputes.png  
  └── letter.png  

---

## 👤 Author

Giorgi Svanidze  
Chemical Engineering + Supply Chain @ Case Western Reserve University
