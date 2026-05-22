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
# SIDEBAR: PERSISTENT STATE INITIALIZATION
# ==========================================
if "current_age" not in st.session_state: st.session_state.current_age = 40
if "monthly_burn" not in st.session_state: st.session_state.monthly_burn = 100000
if "annual_spikes" not in st.session_state: st.session_state.annual_spikes = 240000
if "equity_base" not in st.session_state: st.session_state.equity_base = 12000000
if "debt_base" not in st.session_state: st.session_state.debt_base = 9500000
if "metals_base" not in st.session_state: st.session_state.metals_base = 3000000
if "real_estate_base" not in st.session_state: st.session_state.real_estate_base = 15000000
if "home_loan_base" not in st.session_state: st.session_state.home_loan_base = 4500000
if "other_loan_base" not in st.session_state: st.session_state.other_loan_base = 800000

st.sidebar.title("🛡️ The Reality Vault")
st.sidebar.markdown("Select a secure compartment to calibrate your parameters. Other categories will auto-hide to preserve space.")

# Segmented navigator for clean preservation of space
active_drawer = st.sidebar.radio(
    "Go To Drawer:",
    ["📉 1. Your Costs", "💰 2. Your Money", "⚠️ 3. Your Loans"],
    label_visibility="collapsed"
)

st.sidebar.divider()

# --- DRAWER 1: YOUR COSTS ---
if active_drawer == "📉 1. Your Costs":
    st.sidebar.subheader("📉 Your Costs")
    st.sidebar.markdown("<small style='color: #94a3b8;'>Your profile demographics and essential lifestyle outlays.</small>", unsafe_allow_html=True)
    
    st.session_state.current_age = st.sidebar.number_input(
        "Your Current Age (Years)",
        min_value=21, max_value=75, value=st.session_state.current_age, step=1
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 Age baseline locked at {st.session_state.current_age} years old</div>', unsafe_allow_html=True)

    st.session_state.monthly_burn = st.sidebar.number_input(
        "Standard Monthly Expenses (₹)", 
        min_value=10000, max_value=1000000, value=st.session_state.monthly_burn, step=10000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.monthly_burn)} per month</div>', unsafe_allow_html=True)

    st.session_state.annual_spikes = st.sidebar.number_input(
        "Annual Big Spikes (Insurance, Fees, etc.) (₹)", 
        min_value=0, max_value=5000000, value=st.session_state.annual_spikes, step=20000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.annual_spikes)} per year</div>', unsafe_allow_html=True)

# --- DRAWER 2: YOUR MONEY ---
elif active_drawer == "💰 2. Your Money":
    st.sidebar.subheader("💰 Your Money")
    st.sidebar.markdown("<small style='color: #94a3b8;'>Every scrap of net assets built up so far.</small>", unsafe_allow_html=True)
    
    st.session_state.equity_base = st.sidebar.number_input(
        "Stocks & Mutual Funds (₹)", 
        min_value=0, value=st.session_state.equity_base, step=500000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.equity_base)}</div>', unsafe_allow_html=True)

    st.session_state.debt_base = st.sidebar.number_input(
        "Fixed Deposits / EPF / PPF (₹)", 
        min_value=0, value=st.session_state.debt_base, step=500000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.debt_base)}</div>', unsafe_allow_html=True)

    st.session_state.metals_base = st.sidebar.number_input(
        "Gold & Silver (₹)", 
        min_value=0, value=st.session_state.metals_base, step=100000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.metals_base)}</div>', unsafe_allow_html=True)

    st.session_state.real_estate_base = st.sidebar.number_input(
        "Current Home Market Value (₹)", 
        min_value=0, value=st.session_state.real_estate_base, step=1000000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.real_estate_base)}</div>', unsafe_allow_html=True)

# --- DRAWER 3: YOUR LOANS ---
elif active_drawer == "⚠️ 3. Your Loans":
    st.sidebar.subheader("⚠️ Your Loans")
    st.sidebar.markdown("<small style='color: #94a3b8;'>Active debts dragging your timeline down.</small>", unsafe_allow_html=True)
    
    st.session_state.home_loan_base = st.sidebar.number_input(
        "Home Loan Balance Outstanding (₹)", 
        min_value=0, value=st.session_state.home_loan_base, step=500000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.home_loan_base)}</div>', unsafe_allow_html=True)

    st.session_state.other_loan_base = st.sidebar.number_input(
        "Other Loans (Car, Personal, Credit) (₹)", 
        min_value=0, value=st.session_state.other_loan_base, step=100000
    )
    st.sidebar.markdown(f'<div class="indian-words">👉 {format_indian_words(st.session_state.other_loan_base)}</div>', unsafe_allow_html=True)


# ==========================================
# MAIN DASHBOARD: THE CRISIS TEST
# ==========================================
st.title("The Pink Slip Index")
st.markdown("Your interactive survival sandbox. Adjust the parameters below to gauge your uncompromised safety margin if your salary engine abruptly stops tomorrow.")

st.divider()

# --- CRISIS HEADLINE & RESET ENGINE ---
col_head, col_btn = st.columns([5, 1])
with col_head:
    st.subheader("🚨 The Crisis Test")
    st.markdown("Drag these sliders into negative zones to simulate market and lifestyle shocks.")

if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False

with col_btn:
    st.write("") 
    if st.button("🔄 Reset Crisis Test", use_container_width=True):
        st.session_state.reset_trigger = not st.session_state.reset_trigger

# --- THE GRIPPING CRISIS SLIDERS ---
col_market, col_career = st.columns(2)

with col_market:
    st.markdown("### Market Meltdowns")
    equity_shift = st.slider(
        "Stock Market Collapse / Rally (%)", 
        min_value=-50, max_value=30, value=0, step=5,
        key=f"equity_slider_{st.session_state.reset_trigger}"
    )
    
    if equity_shift == 0:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟢 Normal Market Action</span>", unsafe_allow_html=True)
    elif equity_shift == -10:
        st.markdown("<span class='crisis-text' style='color:#facc15;'>⚠️ Standard Market Correction</span>", unsafe_allow_html=True)
    elif -30 <= equity_shift < -10:
        st.markdown("<span class='crisis-text' style='color:#f97316;'>🔥 Severe Tech & Structural Sector Crash</span>", unsafe_allow_html=True)
    elif equity_shift < -30:
