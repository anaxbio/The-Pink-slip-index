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
    .metric-title { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; margin-bottom: 10px; }
    .metric-value { color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin-bottom: 5px; }
    .metric-sub { color: #38bdf8; font-size: 0.85rem; font-weight: 500; }
    .hero-banner { border-radius: 10px; padding: 24px; text-align: center; margin-bottom: 25px; border: 1px solid dashed; }
    .hero-title { font-size: 2.8rem; font-weight: 800; margin: 0; }
    .hero-subtitle { font-size: 1.1rem; font-weight: 500; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

def format_indian_words(number):
    if number == 0: return "Zero Rupees"
    crores = number // 10000000
    lakhs = (number % 10000000) // 100000
    thousands = (number % 100000) // 1000
    rupees = number % 1000
    result = []
    if crores > 0: result.append(f"{crores} Crore")
    if lakhs > 0: result.append(f"{lakhs} Lakh")
    if thousands > 0: result.append(f"{thousands} Thousand")
    if rupees > 0 or not result: result.append(f"{rupees} Rupees")
    return " ".join(result)

# ==========================================
# SIMULATION ENGINE
# ==========================================
def run_simulation(equity, debt, metals, monthly_burn, annual_spikes, rent=0):
    sim_equity = equity
    sim_debt = debt
    sim_metals = metals
    active_burn = monthly_burn + (annual_spikes/12) + rent
    
    # Debt Clearing Hierarchy
    remaining_debt = st.session_state.home_loan_base + st.session_state.other_loan_base
    for pool in [sim_debt, sim_equity, sim_metals]:
        take = min(pool, remaining_debt)
        pool -= take
        remaining_debt -= take
    
    # Loop
    months = 0
    while months < 600:
        sim_equity *= (1 + (0.10/12))
        sim_debt *= (1 + (0.06/12))
        sim_metals *= (1 + (0.05/12))
        pool = sim_equity + sim_debt + sim_metals
        if pool < active_burn: break
        pool -= active_burn
        months += 1
        if months % 12 == 0: active_burn *= 1.06
    
    return months / 12, st.session_state.current_age + (months / 12)

# ==========================================
# SIDEBAR / STATE
# ==========================================
if "current_age" not in st.session_state: st.session_state.current_age = 40
# ... [Initialize other session_states as before] ...
# [I have abbreviated the sidebar setup to focus on the fix]
st.sidebar.title("🛡️ The Reality Vault")
# ... [Include inputs for Costs, Money, Loans] ...

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.title("The Pink Slip Index")
st.session_state.current_age = st.number_input("⚡ Enter Your Current Age", min_value=21, max_value=75, value=40)

# SLIDERS & ENGINE
equity_shift = st.slider("Stock Market Collapse / Rally (%)", -50, 30, 0, 5)
metals_shift = st.slider("Gold & Silver Collapse / Rally (%)", -20, 40, 0, 5)
expense_shift = st.slider("Monthly Family Expense Spike (₹)", 0, 150000, 0, 10000)

# SCENARIO A: IMMEDIATE SHIELD (Keep Home)
immediate_years, immediate_age = run_simulation(
    st.session_state.equity_base * (1 + equity_shift/100),
    st.session_state.debt_base,
    st.session_state.metals_base * (1 + metals_shift/100),
    st.session_state.monthly_burn + expense_shift,
    st.session_state.annual_spikes
)

# SCENARIO B: TOTAL SHIELD (Sell Home - use 3% yield as rent)
rent_estimate = (st.session_state.real_estate_base * 0.03) / 12
total_years, total_age = run_simulation(
    st.session_state.equity_base * (1 + equity_shift/100),
    st.session_state.debt_base + st.session_state.real_estate_base,
    st.session_state.metals_base * (1 + metals_shift/100),
    st.session_state.monthly_burn + expense_shift,
    st.session_state.annual_spikes,
    rent=rent_estimate
)

# VISUALS
st.divider()
st.markdown(f"""
    <div class="hero-banner" style="background-color: #064e3b; border: 1px solid #10b981; color: #ecfdf5;">
        <div class="hero-subtitle">PINK SLIP PROOF STATUS</div>
        <div class="hero-title">You are secure until Age {int(total_age)}</div>
    </div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Immediate Shield (Status Quo)</div>
            <div class="metric-value">{int(immediate_years * 12)} Mos ({immediate_years:.1f} Yrs)</div>
            <div class="metric-sub">Portfolio gain - inflation 6% (Keeping your home roof intact)</div>
        </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Shield (If Home is Sold)</div>
            <div class="metric-value">{int(total_years * 12)} Mos ({total_years:.1f} Yrs)</div>
            <div class="metric-sub">The absolute maximum age your assets last if you liquidate property</div>
        </div>
    """, unsafe_allow_html=True)
