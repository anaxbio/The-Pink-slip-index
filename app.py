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
    .indian-words {
        color: #38bdf8;
        font-size: 0.85rem;
        margin-top: -5px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    .crisis-text {
        font-weight: bold;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTION: INDIAN CURRENCY TO WORDS
# ==========================================
def format_indian_words(number):
    if number == 0:
        return "Zero Rupees"
    
    crores = number // 10000000
    remainder = number % 10000000
    lakhs = remainder // 100000
    remainder = remainder % 100000
    thousands = remainder // 1000
    rupees = remainder % 1000
    
    result = []
    if crores > 0:
        result.append(f"{crores} Crore" + ("s" if crores > 1 else ""))
    if lakhs > 0:
        result.append(f"{lakhs} Lakh" + ("s" if lakhs > 1 else ""))
    if thousands > 0:
        result.append(f"{thousands} Thousand")
    if rupees > 0 or len(result) == 0:
        result.append(f"{rupees} Rupee" + ("s" if rupees > 1 or rupees == 0 else ""))
        
    return " ".join(result)

# ==========================================
# SIDEBAR: CLEAN EXPANDER COMPRESSION
# ==========================================
st.sidebar.title("🛡️ The Reality Vault")
st.sidebar.markdown("Establish your baseline before running stress tests.")

# --- EXPANDER 1: OUTFLOWS ---
with st.sidebar.expander("📁 1. What it Costs to Live", expanded=True):
    monthly_burn = st.number_input(
        "Monthly Household Expenses (₹)", 
        min_value=10000, max_value=1000000, value=100000, step=10000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(monthly_burn)}</div>', unsafe_allow_html=True)

    annual_spikes = st.number_input(
        "Annual Large Expenses (Insurance, School Fees) (₹)", 
        min_value=0, max_value=5000000, value=240000, step=20000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(annual_spikes)}</div>', unsafe_allow_html=True)

# --- EXPANDER 2: ASSETS ---
with st.sidebar.expander("📁 2. Your Current Assets", expanded=False):
    equity_base = st.number_input(
        "Stocks & Mutual Funds (₹)", 
        min_value=0, value=12000000, step=500000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(equity_base)}</div>', unsafe_allow_html=True)

    debt_base = st.number_input(
        "Fixed Deposits / EPF / PPF (₹)", 
        min_value=0, value=9500000, step=500000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(debt_base)}</div>', unsafe_allow_html=True)

    metals_base = st.number_input(
        "Gold & Silver (₹)", 
        min_value=0, value=3000000, step=100000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(metals_base)}</div>', unsafe_allow_html=True)

    real_estate_base = st.number_input(
        "Your Home Value (₹)", 
        min_value=0, value=15000000, step=1000000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(real_estate_base)}</div>', unsafe_allow_html=True)

# --- EXPANDER 3: LIABILITIES ---
with st.sidebar.expander("📁 3. Debts & Loans", expanded=False):
    home_loan_base = st.number_input(
        "Home Loan Outstanding (₹)", 
        min_value=0, value=4500000, step=500000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(home_loan_base)}</div>', unsafe_allow_html=True)

    other_loan_base = st.number_input(
        "Other Loans (Car / Personal) (₹)", 
        min_value=0, value=800000, step=100000
    )
    st.markdown(f'<div class="indian-words">👉 {format_indian_words(other_loan_base)}</div>', unsafe_allow_html=True)


# ==========================================
# MAIN DASHBOARD: THE CRISIS TEST
# ==========================================
st.title("The Pink Slip Index")
st.markdown("Your interactive survival sandbox. Adjust the parameters below to gauge your uncompromised safety margin if your salary engine abruptly stops tomorrow.")

st.divider()

# --- THE GRIPPING CRISIS SLIDERS ---
st.subheader("🚨 The Crisis Test")
st.markdown("Drag these sliders into negative zones to simulate market and lifestyle shocks.")

col_market, col_career = st.columns(2)

with col_market:
    st.markdown("### Market Meltdowns")
    equity_shift = st.slider("Stock Market Collapse / Rally (%)", min_value=-50, max_value=30, value=0, step=5)
    
    # Dynamic text feedback for the Equity Crisis Slider
    if equity_shift == 0:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟢 Normal Market Action</span>", unsafe_allow_html=True)
    elif equity_shift == -10:
        st.markdown("<span class='crisis-text' style='color:#facc15;'>⚠️ Standard Market Correction</span>", unsafe_allow_html=True)
    elif -30 <= equity_shift < -10:
        st.markdown("<span class='crisis-text' style='color:#f97316;'>🔥 Severe Tech & Structural Sector Crash</span>", unsafe_allow_html=True)
    elif equity_shift < -30:
        st.markdown("<span class='crisis-text' style='color:#ef4444;'>🚨 Absolute Global Financial Crisis (2008 Style)</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#4ade80;'>🚀 Sudden Post-Election Bull Run</span>", unsafe_allow_html=True)

    st.write("") # Spacer
    metals_shift = st.slider("Gold & Silver Volatility (%)", min_value=-20, max_value=40, value=0, step=5)
    if metals_shift > 0:
        st.markdown("<span class='crisis-text' style='color:#4ade80;'>🪙 Gold acting as a defensive flight-to-safety shield</span>", unsafe_allow_html=True)
    elif metals_shift < 0:
        st.markdown("<span class='crisis-text' style='color:#ef4444;'>📉 Rare liquidity squeeze tracking global panic</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟡 Metals holding steady baseline intrinsic value</span>", unsafe_allow_html=True)

with col_career:
    st.markdown("### Lifestyle Cash Drains")
    expense_shift = st.slider("Sudden Family Expense Shock (Monthly Spike) (₹)", min_value=0, max_value=150000, value=0, step=10000)
    if expense_shift > 0:
        st.markdown(f"<span class='crisis-text' style='color:#f97316;'>💸 Simulating a recurring ₹{expense_shift:,.0f} drain (Medical emergencies / Dependent parent care / School fee hikes)</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟢 Lifestyle operating at optimized baseline burn</span>", unsafe_allow_html=True)

    st.write("") # Spacer
    re_liquidation = st.slider("Desperation Play: Liquidate Your Home (₹ Realized Capital)", min_value=0, max_value=int(real_estate_base), value=0, step=1000000)
    if re_liquidation > 0:
        st.markdown(f"<span class='crisis-text' style='color:#ef4444;'>🏠 Selling home under duress. Injecting ₹{re_liquidation:,.0f} cash into the safety pool but stripping your physical estate asset.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🏡 Home asset remains untouched and intact</span>", unsafe_allow_html=True)


# ==========================================
# THE MATHEMATICAL ENGINE
# ==========================================
adj_equity = equity_base * (1 + (equity_shift / 100))
adj_metals = metals_base * (1 + (metals_shift / 100))
adj_debt = debt_base  
adj_home_value = real_estate_base - re_liquidation

# Process standardized monthly burn (combining base cost + annualized bulk cost broken down monthly)
standardized_annual_monthly_addon = annual_spikes / 12
adj_monthly_burn = monthly_burn + expense_shift + standardized_annual_monthly_addon

# Process assets vs liabilities
total_debts = home_loan_base + other_loan_base
total_liquid_assets = adj_equity + adj_debt + adj_metals + re_liquidation
net_liquid_buffer = total_liquid_assets - total_debts

# 1. Pink Slip Runway Calculation
if adj_monthly_burn > 0:
    if net_liquid_buffer > 0:
        runway_months = net_liquid_buffer / adj_monthly_burn
    else:
        runway_months = 0.0
else:
    runway_months = 999.9

# 2. Retirement Lockdown Target
target_fire_corpus = ((adj_monthly_burn * 12) * 25) + total_debts
total_assets_combined = total_liquid_assets + adj_home_value
if target_fire_corpus > 0:
    old_age_safety_pct = (total_assets_combined / target_fire_corpus) * 100
else:
    old_age_safety_pct = 100.0

# 3. Walk-Away Metric
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
            <div class="metric-sub">Survival timeline (Includes prorated annual expenses)</div>
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
            <div class="metric-sub">1.00 = 10-year debt-free runway window achieved</div>
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
