import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="The Career Shield | Prototype",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the "Snazzy" Dark/Premium look
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .metric-sub {
        color: #38bdf8;
        font-size: 0.85rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR: BASELINE ONBOARDING
# ==========================================
st.sidebar.title("🛡️ The Setup Vault")
st.sidebar.markdown("Enter your baseline operational numbers.")

st.sidebar.header("1. Operational Burn")
monthly_burn = st.sidebar.number_input(
    "Current Monthly Expenses (₹)", 
    min_value=10000, max_value=1000000, value=100000, step=10000
)

st.sidebar.header("2. Asset Baseline")
equity_base = st.sidebar.number_input(
    "Domestic Equities (₹)", 
    min_value=0, value=12000000, step=500000
)
debt_base = st.sidebar.number_input(
    "Fixed Income & Debt (₹)", 
    min_value=0, value=9500000, step=500000
)
metals_base = st.sidebar.number_input(
    "Precious Metals Hedge (₹)", 
    min_value=0, value=3000000, step=100000
)
real_estate_base = st.sidebar.number_input(
    "Illiquid Real Estate (₹)", 
    min_value=0, value=15000000, step=1000000
)

# ==========================================
# MAIN DASHBOARD: THE SANDBOX
# ==========================================
st.title("The Career Shield Dashboard")
st.markdown("Your interactive financial heart-rate monitor. Adjust the manual stress-test sliders below to see how market volatility and career decisions impact your true structural runway.")

st.divider()

# --- THE STRESS TEST SLIDERS (MANUAL OVERRIDES) ---
st.subheader("🎛️ The 'What-If' Sandbox")
st.markdown("Use these sliders to simulate real-world shifts without connecting to a live data feed.")

col_market, col_career = st.columns(2)

with col_market:
    st.markdown("**Market Stress Simulator**")
    equity_shift = st.slider("Equities Market Shift (%)", min_value=-50, max_value=50, value=0, step=1)
    metals_shift = st.slider("Precious Metals Shift (%)", min_value=-30, max_value=50, value=0, step=1)

with col_career:
    st.markdown("**Career & Life Stress Simulator**")
    expense_shift = st.slider("Monthly Expense Shift (₹)", min_value=-50000, max_value=100000, value=0, step=5000)
    re_liquidation = st.slider("Simulate Real Estate Sale (₹ to Liquid)", min_value=0, max_value=int(real_estate_base), value=0, step=500000)

# ==========================================
# THE MATHEMATICAL ENGINE
# ==========================================
# Calculate adjusted values based on manual slider inputs
adj_equity = equity_base * (1 + (equity_shift / 100))
adj_metals = metals_base * (1 + (metals_shift / 100))
adj_debt = debt_base  # Assuming fixed income doesn't swing wildly short-term

# Total liquid capital available for runway (plus any simulated RE sales)
total_liquid_corpus = adj_equity + adj_debt + adj_metals + re_liquidation
adj_monthly_burn = monthly_burn + expense_shift

# Core Metrics Calculations
if adj_monthly_burn > 0:
    immediate_runway_months = total_liquid_corpus / adj_monthly_burn
else:
    immediate_runway_months = 999.9

# Coast-FIRE Target (using a standard 4% withdrawal rule / 25x multiple of annual burn)
target_fire_corpus = (adj_monthly_burn * 12) * 25
if target_fire_corpus > 0:
    coast_fire_pct = (total_liquid_corpus / target_fire_corpus) * 100
else:
    coast_fire_pct = 100.0

# Freedom Index (Scale of 0.00 to 1.00 based on achieving 300 months of runway)
freedom_index = min(immediate_runway_months / 300, 1.0)

# ==========================================
# VISUALIZING THE METRICS
# ==========================================
st.divider()
st.subheader("📊 Your Calibrated Reality")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Immediate Shield (Runway)</div>
            <div class="metric-value">{immediate_runway_months:,.1f} <span style="font-size: 1rem; color: #94a3b8;">Months</span></div>
            <div class="metric-sub">Absolute survival at current burn</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Coast-FIRE Status</div>
            <div class="metric-value">{coast_fire_pct:,.1f}%</div>
            <div class="metric-sub">Progress toward total structural independence</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">The Freedom Index</div>
            <div class="metric-value">{freedom_index:,.2f} <span style="font-size: 1rem; color: #94a3b8;">/ 1.00</span></div>
            <div class="metric-sub">1.00 = Absolute Sovereignty</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# DYNAMIC PORTFOLIO TABLE
# ==========================================
st.write("")
st.write("")
st.subheader("🔄 Adjusted Portfolio Baseline")

# Create a clean dataframe for the adjusted portfolio
df_portfolio = pd.DataFrame({
    "Asset Class": ["Domestic Equities", "Fixed Income & Debt", "Precious Metals", "Illiquid Real Estate"],
    "Baseline Value (₹)": [equity_base, debt_base, metals_base, real_estate_base],
    "Simulated Adjustment (₹)": [adj_equity - equity_base, 0, adj_metals - metals_base, -re_liquidation],
    "New Active Value (₹)": [adj_equity, adj_debt, adj_metals, real_estate_base - re_liquidation]
})

st.dataframe(
    df_portfolio.style.format({
        "Baseline Value (₹)": "{:,.0f}",
        "Simulated Adjustment (₹)": "{:+,.0f}",
        "New Active Value (₹)": "{:,.0f}"
    }), 
    use_container_width=True,
    hide_index=True
)

# ==========================================
# LEAD CAPTURE / FUNNEL FOOTER
# ==========================================
st.divider()
st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <h4 style="color: #cbd5e1;">Tired of moving the sliders manually?</h4>
        <p style="color: #94a3b8; font-size: 0.95rem;">Join the private vault. We map your baselines to real-world market closing data and deliver your exact runway index to your inbox every Sunday evening.</p>
    </div>
""", unsafe_allow_html=True)

# Simple text input for email capture (can be connected to a webhook, formsubmit, or DB later)
col_sub1, col_sub2, col_sub3 = st.columns([1, 2, 1])
with col_sub2:
    with st.form("subscription_form"):
        email = st.text_input("Enter your secure email to get the Sunday Report:")
        submit = st.form_submit_button("Lock in my Dashboard")
        if submit and email:
            st.success("Access requested. Welcome to the vault.")
