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
    st.markdown(f'
