import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="The Pink Slip Index",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the Premium Dark Dashboard
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
# SIDEBAR: THE INPUT VAULT
# ==========================================
st.sidebar.title("🛡️ The Reality Vault")
st.sidebar.markdown("Enter your baseline operational numbers.")

st.sidebar.header("1. Your Current Monthly Cost")
monthly_burn = st.sidebar.number_input(
    "Family Expenses Per Month (₹)", 
    min_value=10000, max_value=1000000, value=100000, step=10000
)

st.sidebar.header("2. Money You Already Made")
equity_base = st.sidebar.number_input(
    "Stocks & Mutual Funds (₹)", 
    min_value=0, value=12000000, step=500000
)
debt_base = st.sidebar.number_input(
    "Fixed Deposits / EPF / PPF (₹)", 
    min_value=0, value=9500000, step=500000
)
metals_base = st.sidebar.number_input(
    "Gold & Silver (₹)", 
    min_value=0, value=3000000, step=100000
)
real_estate_base = st.sidebar.number_input(
    "Your Home Value (₹)", 
    min_value=0, value=15000000, step=1000000
)

st.sidebar.header("3. Debts & Loans")
home_loan_base = st.sidebar.number_input(
    "Home Loan Outstanding (₹)", 
    min_value=0, value=4500000, step=500000
)
other_loan_base = st.sidebar.number_input(
    "Other Loans (Car / Personal) (₹)", 
    min_value=0, value=800000, step=100000
)

# ==========================================
# MAIN DASHBOARD: THE SANDBOX
# ==========================================
st.title("The Pink Slip Index")
st.markdown("Your interactive survival sandbox. Adjust the sliders below to see exactly what happens to your family's lifestyle if the primary salary stops tomorrow.")

st.divider()

# --- THE STRESS TEST SLIDERS ---
st.subheader("🎛️ The 'What-If' Crash Simulator")

col_market, col_career = st.columns(2)

with col_market:
    st.markdown("**Simulate Market Crashes**")
    equity_shift = st.slider("Stock Market Crash/Rally (%)", min_value=-50, max_value=50, value=0, step=1)
    metals_shift = st.slider("Gold Price Shift (%)", min_value=-30, max_value=50, value=0, step=1)

with col_career:
    st.markdown("**Simulate Sudden Life Emergencies**")
    expense_shift = st.slider("Sudden Monthly Expense Spike (₹)", min_value=-50000, max_value=100000, value=0, step=5000)
    re_liquidation = st.slider("Sell Home to Get Quick Cash (₹)", min_value=0, max_value=int(real_estate_base), value=0, step=500000)

# ==========================================
# THE MATHEMATICAL ENGINE
# ==========================================
adj_equity = equity_base * (1 + (equity_shift / 100))
adj_metals = metals_base * (1 + (metals_shift / 100))
adj_debt = debt_base  
adj_home_value = real_estate_base - re_liquidation

# Calculation of True Liquid Capital minus immediate debts
total_debts = home_loan_base + other_loan_base
total_liquid_assets = adj_equity + adj_debt + adj_metals + re_liquidation
net_liquid_buffer = total_liquid_assets - total_debts
adj_monthly_burn = monthly_burn + expense_shift

# 1. Pink Slip Runway (Runway in Months based on Net Liquid Buffer)
if adj_monthly_burn > 0:
    if net_liquid_buffer > 0:
        runway_months = net_liquid_buffer / adj_monthly_burn
    else:
        runway_months = 0.0  # Immediate financial danger zone
else:
    runway_months = 999.9

# 2. Retirement Lockdown Target (using standard 25x annual burn multiple + outstanding loans)
target_fire_corpus = ((adj_monthly_burn * 12) * 25) + total_debts
total_assets_combined = total_liquid_assets + adj_home_value
if target_fire_corpus > 0:
    old_age_safety_pct = (total_assets_combined / target_fire_corpus) * 100
else:
    old_age_safety_pct = 100.0

# 3. Walk-Away Metric (Scale of 0.00 to 1.00 based on a 10-year / 120-month clear window)
leverage_score = min(runway_months / 120, 1.0) if runway_months > 0 else 0.0

# ==========================================
# VISUALIZING THE METRICS
# ==========================================
st.divider()
st.subheader("📊 Your Reality")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pink Slip Runway</div>
            <div class="metric-value">{runway_months:,.1f} <span style="font-size: 1rem; color: #94a3b8;">Months</span></div>
            <div class="metric-sub">Net survival duration after clearing outstanding loans</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Retirement Lockdown</div>
            <div class="metric-value">{old_age_safety_pct:,.1f}%</div>
            <div class="metric-sub">How close old age + debts are to being fully funded</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">The Walk-Away Metric</div>
            <div class="metric-value">{leverage_score:,.2f} <span style="font-size: 1rem; color: #94a3b8;">/ 1.00</span></div>
            <div class="metric-sub">1.00 = Debt-free power to quit whenever you want</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ADJUSTED PORTFOLIO & LIABILITIES BASELINE
# ==========================================
st.write("")
st.write("")
st.subheader("🔄 What Your Balance Sheet Looks Like Now")

df_portfolio = pd.DataFrame({
    "Asset Class / Liability": ["Stocks & Mutual Funds", "Fixed Income & Deposits", "Gold & Silver", "Remaining Home Value", "⚠️ Outstanding Loans (Debt)"],
    "Your Baseline (₹)": [equity_base, debt_base, metals_base, real_estate_base, total_debts],
    "Simulated Change (₹)": [adj_equity - equity_base, 0, adj_metals - metals_base, -re_liquidation, 0],
    "Active Reality Value (₹)": [adj_equity, adj_debt, adj_metals, adj_home_value, total_debts]
})

st.dataframe(
    df_portfolio.style.format({
        "Your Baseline (₹)": "{:,.0f}",
        "Simulated Change (₹)": "{:+,.0f}",
        "Active Reality Value (₹)": "{:,.0f}"
    }), 
    use_container_width=True,
    hide_index=True
)

# ==========================================
# FOOTER FUNNEL
# ==========================================
st.divider()
st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <h4 style="color: #cbd5e1;">Tired of moving these sliders manually?</h4>
        <p style="color: #94a3b8; font-size: 0.95rem;">Join the private vault. We track your assets against real-world market closes, factor in your active EMI drains, and deliver your updated survival timelines every Sunday night.</p>
    </div>
""", unsafe_allow_html=True)

col_sub1, col_sub2, col_sub3 = st.columns([1, 2, 1])
with col_sub2:
    with st.form("subscription_form"):
        email = st.text_input("Enter your secure email to request an invite:")
        submit = st.form_submit_button("Request Private Access")
        if submit and email:
            st.success("Access requested. Welcome to the vault.")
