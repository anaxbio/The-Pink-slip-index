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

# Custom CSS for Premium Dark UI & Typography
st.markdown("""
    <style>
    .metric-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-title { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; font-weight: 600; margin-bottom: 10px; }
    .metric-value { color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin-bottom: 5px; }
    .metric-sub { color: #38bdf8; font-size: 0.85rem; font-weight: 500; }
    .hero-banner { border-radius: 10px; padding: 24px; text-align: center; margin-bottom: 25px; border: 1px solid #10b981; background-color: #064e3b; color: #ecfdf5; }
    .hero-title { font-size: 2.5rem; font-weight: 800; margin: 0; }
    .hero-subtitle { font-size: 1.1rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# STATE INITIALIZATION
# ==========================================
defaults = {
    "current_age": 40, "monthly_burn": 100000, "annual_spikes": 240000,
    "equity_base": 12000000, "debt_base": 9500000, "metals_base": 3000000,
    "real_estate_base": 15000000, "home_loan_base": 4500000, "other_loan_base": 800000
}
for key, val in defaults.items():
    if key not in st.session_state: st.session_state[key] = val

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("🛡️ The Reality Vault")
drawer = st.sidebar.radio("Navigate:", ["📉 1. Costs", "💰 2. Money", "⚠️ 3. Loans"])
if drawer == "📉 1. Costs":
    st.session_state.monthly_burn = st.sidebar.number_input("Monthly Expenses (₹)", value=st.session_state.monthly_burn, step=10000)
    st.session_state.annual_spikes = st.sidebar.number_input("Annual Spikes (₹)", value=st.session_state.annual_spikes, step=20000)
elif drawer == "💰 2. Money":
    st.session_state.equity_base = st.sidebar.number_input("Stocks (₹)", value=st.session_state.equity_base, step=500000)
    st.session_state.debt_base = st.sidebar.number_input("Fixed Deposits (₹)", value=st.session_state.debt_base, step=500000)
    st.session_state.metals_base = st.sidebar.number_input("Gold (₹)", value=st.session_state.metals_base, step=100000)
    st.session_state.real_estate_base = st.sidebar.number_input("Home Value (₹)", value=st.session_state.real_estate_base, step=1000000)
elif drawer == "⚠️ 3. Loans":
    st.session_state.home_loan_base = st.sidebar.number_input("Home Loan (₹)", value=st.session_state.home_loan_base, step=500000)
    st.session_state.other_loan_base = st.sidebar.number_input("Other Loans (₹)", value=st.session_state.other_loan_base, step=100000)

# ==========================================
# DASHBOARD
# ==========================================
st.title("The Pink Slip Index")
st.session_state.current_age = st.number_input("⚡ Current Age", value=st.session_state.current_age)
st.divider()

equity_shift = st.slider("Stock Market Change (%)", -50, 30, 0)
metals_shift = st.slider("Gold Change (%)", -20, 40, 0)
expense_shift = st.slider("Monthly Expense Spike (₹)", 0, 150000, 0)
re_liquidation = st.slider("Liquidate Home (₹)", 0, int(st.session_state.real_estate_base), 0)

# ==========================================
# SIMULATION ENGINE
# ==========================================
sim_equity = st.session_state.equity_base * (1 + equity_shift/100)
sim_metals = st.session_state.metals_base * (1 + metals_shift/100)
sim_debt = st.session_state.debt_base
adj_home_value = st.session_state.real_estate_base - re_liquidation
active_burn = st.session_state.monthly_burn + (st.session_state.annual_spikes/12) + expense_shift + ((st.session_state.real_estate_base * 0.03)/12 if re_liquidation > 0 else 0)

# Run Simulation
pool = sim_equity + sim_debt + sim_metals + re_liquidation - (st.session_state.home_loan_base + st.session_state.other_loan_base)
months = 0
while pool >= active_burn and months < 600:
    pool = (pool - active_burn) * (1 + 0.06/12)
    months += 1
    if months % 12 == 0: active_burn *= 1.06

# Long Term Calc
lt_pool = (sim_equity + sim_debt + sim_metals + adj_home_value) - (st.session_state.home_loan_base + st.session_state.other_loan_base)
lt_burn = active_burn
lt_yrs = 0
while lt_pool >= (lt_burn * 12) and lt_yrs < 50:
    lt_pool = (lt_pool - (lt_burn * 12)) * 1.06
    lt_burn *= 1.06
    lt_yrs += 1

# ==========================================
# OUTPUT
# ==========================================
st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-subtitle">PINK SLIP PROOF STATUS</div>
        <div class="hero-title">You are Pink Slip Proof until Age {int(st.session_state.current_age + lt_yrs)}</div>
    </div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
c1.markdown(f"""<div class="metric-card"><div class="metric-title">Immediate Shield</div><div class="metric-value">{months//12} Yrs {months%12} Mos</div><div class="metric-sub">Portfolio gain - inflation 6%</div></div>""", unsafe_allow_html=True)
c2.markdown(f"""<div class="metric-card"><div class="metric-title">Total Shield</div><div class="metric-value">Life Secured until Age {int(st.session_state.current_age + lt_yrs)}</div><div class="metric-sub">If you sell the home for emergency funds</div></div>""", unsafe_allow_html=True)
