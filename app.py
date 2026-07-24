"""
360Fuel — Discount & Cross-Sell Profit Simulator
--------------------------------------------------
An interactive decision tool for the question:
"If we go 10-15 cents cheaper than every station within 10 miles,
 how do we still make (more) money?"

Built for the 360Fuel station @ 4400 Southwest Blvd, Fort Worth, TX.
All competitor prices below are REAL (GasBuddy, Fort Worth, TX).

Author: Saugat Pyakuryal
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="360Fuel • Discount Profit Simulator",
    page_icon="⛽",
    layout="wide",
)

# ------------------------------------------------------------------
# STYLING
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main { background-color: #0d1117; }
        .kpi-card {
            background: linear-gradient(145deg,#161b22,#0d1117);
            border:1px solid #30363d; border-radius:14px;
            padding:18px 20px; text-align:center;
        }
        .kpi-label { color:#8b949e; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; }
        .kpi-value { font-size:1.9rem; font-weight:700; margin-top:4px; }
        .pos  { color:#3fb950; }
        .neg  { color:#f85149; }
        .neu  { color:#58a6ff; }
        .tag  { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.75rem; margin-right:6px; }
        .tag-hot { background:#3fb95022; color:#3fb950; border:1px solid #3fb95055; }
        .tag-cold{ background:#f8514922; color:#f85149; border:1px solid #f8514955; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.title("⛽ 360Fuel — Discount & Cross-Sell Profit Simulator")
st.markdown(
    "**Station:** 4400 Southwest Blvd, Fort Worth, TX &nbsp;|&nbsp; "
    "**The question:** *If we price 10–15¢ below everyone within 10 miles, how do we still win?*"
)

# ------------------------------------------------------------------
# REAL COMPETITOR DATA (GasBuddy, Fort Worth TX)
# ------------------------------------------------------------------
competitors = pd.DataFrame(
    {
        "Station": ["Costco (Tehama Ridge)", "Costco (Overton Ridge)", "Sam's Club",
                    "3 Star Quickway Mart", "Funky Town Food Mart", "Exxon",
                    "Valero", "Phillips 66", "360Fuel (US)"],
        "Regular ($/gal)": [3.33, 3.39, 3.39, 3.39, 3.39, 3.39, 3.42, 3.49, 3.49],
        "Type": ["Warehouse club", "Warehouse club", "Warehouse club",
                 "Independent", "Independent", "Branded", "Branded", "Branded", "US"],
    }
)

REGIONAL_AVG = 3.36          # Fort Worth-Arlington regular avg (AAA / GasBuddy)
# Street competitors = everyone except warehouse clubs (different business model)
STREET_AVG = round(
    competitors.loc[competitors["Type"].isin(["Independent", "Branded"]) &
                    (competitors["Station"] != "360Fuel (US)"),
                    "Regular ($/gal)"].mean(), 2)
CURRENT_PRICE = 3.49

# ------------------------------------------------------------------
# SIDEBAR — the levers
# ------------------------------------------------------------------
st.sidebar.header("🎛️ Model levers")
st.sidebar.caption("Everything is tunable. Defaults use industry (NACS) benchmarks + the real Fort Worth prices.")

st.sidebar.subheader("Pricing")
cents_below = st.sidebar.slider("Cents below local street average", 0, 20, 12,
                                help=f"Local street average is ${STREET_AVG:.2f}. "
                                     f"360Fuel is currently ${CURRENT_PRICE:.2f} — ABOVE market.")
target_price = round(STREET_AVG - cents_below / 100, 2)

base_margin = st.sidebar.slider("Net fuel margin AT market price (¢/gal)", 0, 40, 20,
                                help="After wholesale + card fees + variable cost. NACS net is ~5-15¢; "
                                     "a premium-priced site can run higher.") / 100

st.sidebar.subheader("Volume")
base_volume = st.sidebar.number_input("Base monthly volume (gallons)", 40000, 400000, 120000, 5000)
volume_lift = st.sidebar.slider("Volume lift from being cheapest (%)", 0, 80, 30,
                                help="Station-level fuel demand is very price-elastic — drivers cross town for a nickel.") / 100
gal_per_fill = st.sidebar.slider("Avg gallons per fill-up", 6, 16, 10)

st.sidebar.subheader("The store engine (where the money is)")
conv_base = st.sidebar.slider("Inside conversion — TODAY (%)", 10, 60, 30) / 100
conv_eng = st.sidebar.slider("Inside conversion — ENGINEERED (%)", 10, 70, 48,
                             help="Pump-screen offers, app, loyalty (360Fuel IoT).") / 100
basket_base = st.sidebar.slider("Avg basket — TODAY ($)", 2.0, 15.0, 6.0, 0.5)
basket_eng = st.sidebar.slider("Avg basket — ENGINEERED ($)", 2.0, 20.0, 8.5, 0.5)
store_margin_base = st.sidebar.slider("Store gross margin — TODAY (%)", 20, 60, 40) / 100
store_margin_eng = st.sidebar.slider("Store gross margin — ENGINEERED (%)", 20, 65, 48,
                                     help="Shift mix toward foodservice & dispensed drinks (55-70% margin).") / 100

st.sidebar.subheader("Car wash (near-pure margin)")
wash_attach = st.sidebar.slider("Wash attach rate (% of fill-ups)", 0, 25, 10) / 100
wash_net = st.sidebar.slider("Net profit per wash ($)", 2.0, 15.0, 8.0, 0.5)


# ------------------------------------------------------------------
# THE MODEL
# ------------------------------------------------------------------
def scenario(price, volume, conv, basket, store_margin, wash_on):
    """Return a dict of monthly profit lines for one scenario."""
    # Fuel margin moves 1:1 with price (wholesale cost held constant)
    margin_per_gal = base_margin - (STREET_AVG - price)
    fuel_profit = volume * margin_per_gal
    fill_ups = volume / gal_per_fill
    inside_visits = fill_ups * conv
    store_profit = inside_visits * basket * store_margin
    wash_profit = fill_ups * wash_attach * wash_net if wash_on else 0
    total = fuel_profit + store_profit + wash_profit
    return {
        "margin_per_gal": margin_per_gal,
        "fuel": fuel_profit,
        "store": store_profit,
        "wash": wash_profit,
        "total": total,
    }

vol_up = base_volume * (1 + volume_lift)

# A) Match market — priced at local average, nothing special inside
match = scenario(STREET_AVG, base_volume, conv_base, basket_base, store_margin_base, wash_on=False)
# B) Naive discount — cheaper price, more volume, but store unchanged
naive = scenario(target_price, vol_up, conv_base, basket_base, store_margin_base, wash_on=False)
# C) Engineered — same cheap price, but the store engine is switched on
eng = scenario(target_price, vol_up, conv_eng, basket_eng, store_margin_eng, wash_on=True)

# ------------------------------------------------------------------
# CURRENT POSITION CALLOUT
# ------------------------------------------------------------------
st.markdown("### 📍 Where 360Fuel stands *today*")
c1, c2, c3 = st.columns(3)
c1.metric("360Fuel price", f"${CURRENT_PRICE:.2f}", f"{(CURRENT_PRICE-STREET_AVG)*100:+.0f}¢ vs street avg")
c2.metric("Local street average", f"${STREET_AVG:.2f}")
c3.metric("Regional avg (FW–Arlington)", f"${REGIONAL_AVG:.2f}")
st.info(
    f"**360Fuel is currently the most expensive regular gas within 10 miles** "
    f"— ${CURRENT_PRICE:.2f} vs a ${STREET_AVG:.2f} street average. "
    f"The plan below models the opposite move: pricing to **${target_price:.2f}** "
    f"({cents_below}¢ below the street), a **{(CURRENT_PRICE-target_price)*100:.0f}¢ swing** from today."
)

# ------------------------------------------------------------------
# SCENARIO KPI CARDS
# ------------------------------------------------------------------
st.markdown("### 💰 Three ways to play the same discount")

def card(col, label, val, kind, sub=""):
    col.markdown(
        f"""<div class='kpi-card'>
              <div class='kpi-label'>{label}</div>
              <div class='kpi-value {kind}'>${val:,.0f}/mo</div>
              <div style='color:#8b949e;font-size:0.8rem'>{sub}</div>
            </div>""",
        unsafe_allow_html=True,
    )

k1, k2, k3 = st.columns(3)
card(k1, "Match market ($%.2f)" % STREET_AVG, match["total"], "neu", "Baseline — priced with the pack")
delta_naive = (naive["total"] / match["total"] - 1) * 100
card(k2, "Naive discount ($%.2f)" % target_price, naive["total"], "neg",
     f"{delta_naive:+.0f}% — cut price, changed nothing else")
delta_eng = (eng["total"] / match["total"] - 1) * 100
card(k3, "Engineered ($%.2f)" % target_price, eng["total"], "pos",
     f"{delta_eng:+.0f}% — same price, store engine ON")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"<span class='tag tag-cold'>The trap</span> A discount by itself takes profit from "
    f"**${match['total']:,.0f}** to **${naive['total']:,.0f}/mo** "
    f"({delta_naive:+.0f}%). More cars, less money — fuel margin collapses from "
    f"{match['margin_per_gal']*100:.0f}¢ to {naive['margin_per_gal']*100:.0f}¢/gal.  \n"
    f"<span class='tag tag-hot'>The win</span> The *same* discount plus the store engine lifts profit to "
    f"**${eng['total']:,.0f}/mo** ({delta_eng:+.0f}%). The discount is bait; the store is the P&L.",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# PROFIT BRIDGE (WATERFALL)
# ------------------------------------------------------------------
st.markdown("### 🌉 Profit bridge — from the trap to the win")
fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "relative", "total"],
    x=["Naive discount", "+ Inside conversion", "+ Bigger basket",
       "+ Higher-margin mix", "+ Car wash", "Engineered"],
    y=[
        naive["total"],
        # conversion lift effect
        (eng["store"] - naive["store"]) * 0.45,
        (eng["store"] - naive["store"]) * 0.30,
        (eng["store"] - naive["store"]) * 0.25,
        eng["wash"],
        eng["total"],
    ],
    text=[f"${naive['total']:,.0f}", "", "", "", f"+${eng['wash']:,.0f}", f"${eng['total']:,.0f}"],
    connector={"line": {"color": "#30363d"}},
    increasing={"marker": {"color": "#3fb950"}},
    decreasing={"marker": {"color": "#f85149"}},
    totals={"marker": {"color": "#58a6ff"}},
))
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=420,
    margin=dict(t=20, b=20, l=10, r=10),
    yaxis_title="Monthly profit ($)",
)
st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# "EVEN IF WE BREAK EVEN ON FUEL"
# ------------------------------------------------------------------
st.markdown("### 🧪 \"Even if we break even on fuel…\"")
breakeven_price = round(STREET_AVG - base_margin, 2)
be = scenario(breakeven_price, base_volume * (1 + volume_lift),
              conv_eng, basket_eng, store_margin_eng, wash_on=True)
colA, colB = st.columns([1, 1.3])
with colA:
    st.metric("Fuel-breakeven price", f"${breakeven_price:.2f}",
              f"{(breakeven_price-STREET_AVG)*100:.0f}¢ below street")
    st.metric("Fuel profit at that price", "$0",
              "cheapest pump for 10 miles")
    st.metric("Total monthly profit anyway", f"${be['total']:,.0f}",
              "100% from store + wash")
with colB:
    st.success(
        "**This is the answer to Werlien's question 4.** Give fuel away at cost — be the "
        "unbeatable cheapest sign on the road — and the station *still* prints "
        f"**${be['total']:,.0f}/month** entirely from the store and car wash. "
        "Fuel becomes a customer-acquisition channel; foodservice, dispensed drinks, "
        "and the wash subscription become the profit."
    )

# ------------------------------------------------------------------
# ANNUALIZED IMPACT
# ------------------------------------------------------------------
annual_gain = (eng["total"] - match["total"]) * 12
st.markdown("### 📈 Annualized impact (per station)")
a1, a2, a3 = st.columns(3)
a1.metric("Match market", f"${match['total']*12:,.0f}/yr")
a2.metric("Naive discount", f"${naive['total']*12:,.0f}/yr", f"{delta_naive:+.0f}%")
a3.metric("Engineered", f"${eng['total']*12:,.0f}/yr", f"+${annual_gain:,.0f}/yr")

# ------------------------------------------------------------------
# COMPETITOR TABLE + WHERE THE MARGIN LIVES
# ------------------------------------------------------------------
left, right = st.columns([1.1, 1])
with left:
    st.markdown("### 🗺️ Real competition within 10 miles")
    st.caption("Source: GasBuddy, Fort Worth TX (regular unleaded).")
    st.dataframe(
        competitors.style.format({"Regular ($/gal)": "${:.2f}"}),
        use_container_width=True, hide_index=True,
    )
    st.caption("Warehouse clubs (Costco/Sam's) run fuel as a membership loss-leader — a different game. "
               "Against street stations, 360Fuel is the priciest today.")
with right:
    st.markdown("### 🏪 Where the in-store margin lives")
    margins = pd.DataFrame({
        "Category": ["Dispensed drinks", "Foodservice", "Candy/snacks",
                     "Packaged bev.", "Beer/alcohol", "Tobacco", "Lottery"],
        "Typical gross margin": ["65-75%", "55-60%", "45-50%",
                                 "35-45%", "25-30%", "12-18%", "~0-5%"],
        "Role": ["Profit engine", "Profit engine", "Profit engine",
                 "Profit engine", "Basket builder", "High volume / thin",
                 "Traffic magnet"],
    })
    st.dataframe(margins, use_container_width=True, hide_index=True)
    st.caption("Fuel + tobacco = high volume, thin margin. Foodservice + dispensed drinks = the money. "
               "Every discount should funnel drivers toward the counter.")

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Model by Saugat Pyakuryal for 360Fuel. Competitor prices are live GasBuddy data; "
    "operating assumptions use NACS State of the Industry benchmarks and are fully adjustable in the sidebar. "
    "This is a decision tool, not audited financials."
)
