# 360Fuel — Discount & Cross-Sell Profit Simulator

An interactive decision tool answering: *"If 360Fuel prices 10–15¢ below every station within 10 miles, how do we still make more money?"*

Built for the 360Fuel site at **4400 Southwest Blvd, Fort Worth, TX**, using **live GasBuddy competitor prices** and NACS industry benchmarks. Every assumption is a slider — the viewer can stress-test the strategy live.

**The core finding:** a discount *alone* cuts monthly profit ~27%. The *same* discount, paired with a store-and-car-wash monetization engine, lifts it ~70% (~$274K/yr per station). Even at fuel break-even, the station still prints profit from inside the store.

---

## Run it locally (30 seconds)

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens at `http://localhost:8501`.

---

## Deploy a public link (free) — GitHub + Streamlit Community Cloud

**1. Put these files in a GitHub repo**
   - Create a new repo at https://github.com/new (e.g. `360fuel-profit-simulator`), Public.
   - Upload `app.py`, `requirements.txt`, and this `README.md` (drag-and-drop in the browser works, or use git):
     ```bash
     git init
     git add app.py requirements.txt README.md
     git commit -m "360Fuel profit simulator"
     git branch -M main
     git remote add origin https://github.com/<your-username>/360fuel-profit-simulator.git
     git push -u origin main
     ```

**2. Deploy on Streamlit Community Cloud (free)**
   - Go to https://share.streamlit.io and sign in with GitHub.
   - Click **New app** → pick your repo → branch `main` → main file `app.py` → **Deploy**.
   - In ~1 minute you get a public URL like `https://360fuel-profit-simulator.streamlit.app`.

**3. Send Werlien the link.** He can drag the sliders himself.

---

## What's inside
- Real competitor price table (GasBuddy, Fort Worth) + 360Fuel's current position
- Three-scenario model: *Match market → Naive discount → Engineered discount*
- Live profit-bridge waterfall chart
- "Even if we break even on fuel" panel
- Annualized per-station impact
- In-store margin reference (where the money actually is)

*Model by Saugat Pyakuryal. Decision tool, not audited financials.*
