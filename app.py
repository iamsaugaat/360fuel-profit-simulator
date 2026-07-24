"""
360Fuel — Clean & Tabbed Executive Presentation
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="360Fuel Strategy", page_icon="⛽", layout="wide")

# --- CUSTOM CSS FOR CLEAN METRICS ---
st.markdown("""
    <style>
        .metric-box {
            background-color: #1e1e1e; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #333;
        }
        .metric-title { font-size: 14px; color: #888; text-transform: uppercase; }
        .metric-value { font-size: 32px; font-weight: bold; color: #fff; margin: 10px 0; }
        .metric-sub { font-size: 12px; color: #4CAF50; }
        .metric-sub-neg { font-size: 12px; color: #F44336; }
    </style>
""", unsafe_allow_html=True)

st.title("⛽ 360Fuel: Fort Worth Market Strategy")
st.markdown("**Site:** 4400 Southwest Blvd | **Goal:** Win the 10-mile radius profitably.")
st.markdown("---")

# --- DATA SETUP ---
REGIONAL_AVG = 3.36
STREET_AVG = 3.42
CURRENT_PRICE = 3.49
base_volume = 120000
gal_per_fill = 10

# Create Tabs mapping directly to the CEO's assignment
tab1, tab2, tab3 = st.tabs([
    "1. Margins & The Market", 
    "2. The Discount Strategy", 
    "3. The Break-Even Engine"
])

# ==========================================
# TAB 1: MARGINS & MARKET
# ==========================================
with tab1:
    st.header("1. Margins & Current Market Position")
    st.markdown("Answering: *Research gas station margin categories and typical fuel margins.*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 The 10-Mile Reality")
        st.info(f"**360Fuel is currently the most expensive gas within 10 miles at ${CURRENT_PRICE}.** The street average is ${STREET_AVG}.")
        competitors = pd.DataFrame({
            "Station": ["Costco/Sam's", "Exxon", "Valero", "Phillips 66", "360Fuel (US)"],
            "Price": ["$3.33 - $3.39", "$3.39", "$3.42", "$3.49", "$3.49"],
            "Model": ["Warehouse (Loss Leader)", "Branded", "Branded", "Branded", "Us"]
        })
        st.table(competitors)

    with col2:
        st.subheader("🏪 Where the Margin Actually Lives")
        st.markdown("Fuel yields roughly a **5–15¢ net margin per gallon** after swipe fees. The true profit engine is inside the store:")
        margins = pd.DataFrame({
            "Category": ["Dispensed drinks (Coffee/Fountain)", "Foodservice (Hot food)", "Candy/Snacks", "Packaged Bev", "Tobacco"],
            "Gross Margin": ["65-75%", "55-60%", "45-50%", "35-45%", "12-18%"],
            "Role": ["Profit Engine", "Profit Engine", "Profit Engine", "Profit Engine", "High Volume / Thin Margin"]
        })
        st.table(margins)

# ==========================================
# TAB 2: THE DISCOUNT STRATEGY
# ==========================================
with tab2:
    st.header("2. How Discounts Drive Revenue")
    st.markdown("Answering: *If we are 10-15¢ cheaper than stations around us, how do we win?*")
    
    st.markdown("### Test the Strategy:")
    colA, colB, colC = st.columns(3)
    discount_cents = colA.slider("Discount below street avg (cents):", 0, 20, 12)
    new_price = STREET_AVG - (discount_cents / 100)
    
    conversion_rate = colB.slider("Inside Store Conversion (%):", 20, 60, 48, help="How many people pumping gas walk inside.")
    basket_size = colC.slider("Avg In-Store Spend ($):", 4.00, 15.00, 8.50)

    # Simple Math Logic
    fuel_margin_net = 0.20 - (discount_cents / 100)
    vol_up = base_volume * 1.30 # 30% volume lift from discount
    
    # Scenarios
    # Baseline
    base_fuel_prof = base_volume * 0.20
    base_store_prof = (base_volume / 10) * 0.30 * 6.00 * 0.40
    base_total = base_fuel_prof + base_store_prof
    
    # Engineered (With sliders)
    eng_fuel_prof = vol_up * fuel_margin_net
    eng_store_prof = (vol_up / 10) * (conversion_rate / 100) * basket_size * 0.48
    eng_wash_prof = (vol_up / 10) * 0.10 * 8.00 # 10% car wash attach
    eng_total = eng_fuel_prof + eng_store_prof + eng_wash_prof

    st.markdown("<br>", unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Baseline: Match Market ({STREET_AVG})</div>
            <div class="metric-value">${base_total:,.0f} / mo</div>
            <div class="metric-sub-neg">Standard 30% inside conversion</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Engineered Discount ({new_price:.2f})</div>
            <div class="metric-value">${eng_total:,.0f} / mo</div>
            <div class="metric-sub">Using cheap fuel to bait high-margin store sales</div>
        </div>
        """, unsafe_allow_html=True)

    st.info("💡 **The Takeaway:** A naive discount loses money. But pairing a 12¢ discount with a strong store/wash conversion strategy increases overall monthly profit massively. The discount isn't the product; it's the customer acquisition cost.")

# ==========================================
# TAB 3: THE BREAK-EVEN ENGINE
# ==========================================
with tab3:
    st.header("3. The Break-Even Engine")
    st.markdown("Answering: *Even if we break even on fuel, what else can we tie in to make revenue?*")
    
    st.markdown("### The Extreme Scenario: $0 Fuel Profit")
    
    be_price = STREET_AVG - 0.20
    be_store_prof = (vol_up / 10) * 0.48 * 8.50 * 0.48
    be_wash_prof = (vol_up / 10) * 0.10 * 8.00
    be_total = be_store_prof + be_wash_prof
    
    colX, colY = st.columns([1, 2])
    with colX:
        st.metric("Fuel Price", f"${be_price:.2f}", "-20¢ below street")
        st.metric("Fuel Profit", "$0.00", "Break-even")
        st.metric("Total Monthly Profit", f"${be_total:,.0f}", "100% from store & wash")
        
    with colY:
        st.success("**How we make money when fuel is sold at cost using 360Fuel Technology:**")
        st.markdown("""
        1. **IoT Pump Offers:** Personalized screen offers based on driver history ("Your usual energy drink, 2 for $4 today"). This drives the 48% inside conversion rate.
        2. **Car Wash Subscriptions:** Bundle a free wash with an 8+ gallon fill-up to bait them, then convert to a $19.99/mo subscription. Near pure margin.
        3. **Foodservice & Coffee Push:** A dynamic pricing AI lets us discount fuel aggressively *only* during peak morning coffee hours when in-store margin capture is highest (65-75%).
        4. **Unmanned Retail / Smart Coolers:** We can afford to sell fuel at break-even because our automated retail tech drastically reduces labor overhead compared to the independent stations down the street.
        """)
