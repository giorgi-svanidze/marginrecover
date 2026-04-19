# MarginRecover

MarginRecover is a supply chain analytics tool that helps suppliers identify invalid retailer chargebacks, prioritize disputes, and recover lost revenue.
---

## 🚀 Key Feature

Suppliers lose millions annually to retailer chargebacks — not because they’re wrong, but because they lack structured dispute workflows.

MarginRecover transforms messy deduction data into:
- clear validation decisions  
- prioritized recovery actions  
- and fully documented dispute cases  

It doesn’t just analyze problems — it generates **ready-to-submit dispute letters**, turning a slow, manual process into an automated recovery engine.

---

## 📊 Demo

### Portfolio Dashboard — Revenue leakage visibility  
<img src="images/dashboard.png" width="800"/>

### Dispute Queue — Prioritized recovery pipeline  
<img src="images/disputes.png" width="800"/>

### AI Dispute Letter — Automated claim documentation  
<img src="images/letter.png" width="800"/>

---

## ⚙️ What it does

Retailer OTIF and compliance deductions often leak revenue because:
- finance sees the short pay  
- operations sees the shipment  
- but no one owns dispute execution  

MarginRecover closes this gap by combining:

- rules-based deduction validation  
- evidence-readiness scoring  
- dispute prioritization  
- AI-generated executive summaries  
- AI-generated dispute letters  
- impact simulation for finance and operations leaders  

---

## 🧠 Why this matters

Most suppliers:
- under-dispute valid claims  
- lack structured documentation  
- treat deductions reactively  

MarginRecover enables:
- faster recovery cycles  
- higher dispute win rates  
- data-driven supply chain accountability  

---

## 🛠 Run locally

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
