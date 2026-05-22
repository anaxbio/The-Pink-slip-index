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
        padding: 24px;
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
    .hero-banner {
        border-radius: 10px;
        padding: 24px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid dashed;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    st.sidebar.markdown("<small style='color: #94a3b8;'>Your essential lifestyle outlays and baseline household operational costs.</small>", unsafe_allow_html=True)
    
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
# MAIN DASHBOARD HEADER & VISIBLE AGE ANCHOR
# ==========================================
col_title, col_age_input = st.columns([4, 2])

with col_title:
    st.title("The Pink Slip Index")
    st.markdown("Your interactive survival sandbox. Adjust parameters to gauge your safety margin if your corporate salary engine abruptly stops.")

with col_age_input:
    st.session_state.current_age = st.number_input(
        "⚡ Enter Your Current Age (Years)",
        min_value=21, max_value=75, value=st.session_state.current_age, step=1
    )

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
        st.markdown("<span class='crisis-text' style='color:#ef4444;'>🚨 Absolute Global Financial Crisis (2008 Style)</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#4ade80;'>🚀 Sudden Post-Election Bull Run</span>", unsafe_allow_html=True)

    st.write("") 
    metals_shift = st.slider(
        "Gold & Silver Collapse / Rally (%)", 
        min_value=-20, max_value=40, value=0, step=5,
        key=f"metals_slider_{st.session_state.reset_trigger}"
    )
    if metals_shift > 0:
        st.markdown("<span class='crisis-text' style='color:#4ade80;'>🪙 Gold acting as a defensive flight-to-safety shield</span>", unsafe_allow_html=True)
    elif metals_shift < 0:
        st.markdown("<span class='crisis-text' style='color:#ef4444;'>📉 Rare liquidity squeeze tracking global panic</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟡 Metals holding steady baseline intrinsic value</span>", unsafe_allow_html=True)

with col_career:
    st.markdown("### Lifestyle Cash Drains")
    expense_shift = st.slider(
        "Sudden Family Expense Shock (Monthly Spike) (₹)", 
        min_value=0, max_value=150000, value=0, step=10000,
        key=f"expense_slider_{st.session_state.reset_trigger}"
    )
    if expense_shift > 0:
        st.markdown(f"<span class='crisis-text' style='color:#f97316;'>💸 Simulating a recurring ₹{expense_shift:,.0f} drain (Medical / Dependents / Tuition)</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🟢 Lifestyle operating at optimized baseline burn</span>", unsafe_allow_html=True)

    st.write("") 
    re_liquidation = st.slider(
        "Desperation Play: Liquidate Your Home (₹ Realized Capital)", 
        min_value=0, max_value=int(st.session_state.real_estate_base), value=0, step=1000000,
        key=f"re_slider_{st.session_state.reset_trigger}"
    )
    
    simulated_monthly_rent = 0
    
    if re_liquidation > 0:
        st.markdown(f"<span class='crisis-text' style='color:#ef4444;'>🏠 Selling home under duress. Injecting ₹{re_liquidation:,.0f} cash.</span>", unsafe_allow_html=True)
        st.warning("⚠️ HOMELESS WARNING: Liquidating your house means you must rent a home. Define your emergency rent allocation below.")
        
        suggested_rent = int((st.session_state.real_estate_base * 0.03) / 12)
        
        simulated_monthly_rent = st.number_input(
            "Set Your Emergency Monthly Budget for Alternative Rent (₹)",
            min_value=5000, max_value=500000, value=suggested_rent, step=5000
        )
        st.markdown(f'<div class="indian-words">👉 Rent factored into lifestyle burn: {format_indian_words(simulated_monthly_rent)} per month</div>', unsafe_allow_html=True)
    else:
        st.markdown("<span class='crisis-text' style='color:#94a3b8;'>🏡 Home asset remains untouched and intact</span>", unsafe_allow_html=True)


# ==========================================
# THE MATHEMATICAL SIMULATION ENGINE 
# ==========================================
sim_equity = st.session_state.equity_base * (1 + (equity_shift / 100))
sim_metals = st.session_state.metals_base * (1 + (metals_shift / 100))
sim_debt = st.session_state.debt_base
adj_home_value = st.session_state.real_estate_base - re_liquidation

standardized_annual_monthly_addon = st.session_state.annual_spikes / 12
active_monthly_burn = st.session_state.monthly_burn + expense_shift + standardized_annual_monthly_addon + simulated_monthly_rent

total_debts = st.session_state.home_loan_base + st.session_state.other_loan_base

# Immediate asset settlement for loan matching
remaining_debt_to_clear = total_debts

if sim_debt >= remaining_debt_to_clear:
    sim_debt -= remaining_debt_to_clear
    remaining_debt_to_clear = 0
else:
    remaining_debt_to_clear -= sim_debt
    sim_debt = 0

if remaining_debt_to_clear > 0:
    if sim_equity >= remaining_debt_to_clear:
        sim_equity -= remaining_debt_to_clear
        remaining_debt_to_clear = 0
    else:
        remaining_debt_to_clear -= sim_equity
        sim_equity = 0

if remaining_debt_to_clear > 0:
    if sim_metals >= remaining_debt_to_clear:
        sim_metals -= remaining_debt_to_clear
        remaining_debt_to_clear = 0
    else:
        remaining_debt_to_clear -= sim_metals
        sim_metals = 0

sim_debt += re_liquidation

# --- CORE SIMULATION MONTHLY TIMELINE LOOP ---
runway_months = 0
max_sim_months = 600 

while runway_months < max_sim_months:
    sim_equity *= (1 + (0.10 / 12))
    sim_debt *= (1 + (0.06 / 12))
    sim_metals *= (1 + (0.05 / 12))
    
    total_liquid_pool = sim_equity + sim_debt + sim_metals
    
    if total_liquid_pool < active_monthly_burn:
        break
        
    shortfall = active_monthly_burn
    
    if sim_debt >= shortfall:
        sim_debt -= shortfall
        shortfall = 0
    else:
        shortfall -= sim_debt
        sim_debt = 0
        
    if shortfall > 0:
        if sim_equity >= shortfall:
            sim_equity -= shortfall
            shortfall = 0
        else:
            shortfall -= sim_equity
            sim_equity = 0
            
    if shortfall > 0:
        if sim_metals >= shortfall:
            sim_metals -= shortfall
            shortfall = 0
        else:
            shortfall -= sim_metals
            sim_metals = 0
            
    runway_months += 1
    if runway_months % 12 == 0:
        active_monthly_burn *= 1.06

runway_years = runway_months / 12
age_until_covered = st.session_state.current_age + runway_years

# --- RE-SIMULATE INTEGRATED VALUATION FOR TOTAL LIFETIME SECURITY ---
sim_equity_lt = st.session_state.equity_base * (1 + (equity_shift / 100))
sim_metals_lt = st.session_state.metals_base * (1 + (metals_shift / 100))
sim_debt_lt = st.session_state.debt_base + re_liquidation
sim_home_lt = adj_home_value

lt_monthly_burn = st.session_state.monthly_burn + expense_shift + standardized_annual_monthly_addon + simulated_monthly_rent
lt_debt_remaining = total_debts
funded_years = 0

for yr in range(1, 51):
    combined_lt_pool = (sim_equity_lt + sim_metals_lt + sim_debt_lt + sim_home_lt) - lt_debt_remaining
    annual_cost = lt_monthly_burn * 12
    
    if combined_lt_pool < annual_cost:
        break
        
    sim_debt_lt = (sim_debt_lt + sim_equity_lt + sim_metals_lt + sim_home_lt) - lt_debt_remaining - annual_cost
    sim_equity_lt = 0
    sim_metals_lt = 0
    sim_home_lt = 0
    lt_debt_remaining = 0
    
    sim_debt_lt *= 1.06
    lt_monthly_burn *= 1.06
    funded_years += 1

max_safe_age = min(st.session_state.current_age + funded_years, 100)


# ==========================================
# VISUALIZING THE METRICS
# ==========================================
st.divider()
st.subheader("📊 Your Reality")

display_age_whole_number = int(age_until_covered)

# --- SPLASHED HERO BANNER ---
if runway_years == 0:
    banner_bg = "#7f1d1d"       
    banner_border = "#ef4444"   
    banner_text = "#fef2f2"     
    status_label = "🚨 CRISIS ZONE: Immediate Financial Inundation"
    hero_title_text = "Shield Expired"
elif runway_years < 1.0:
    banner_bg = "#7f1d1d"       
    banner_border = "#ef4444"   
    banner_text = "#fef2f2"     
    status_label = "🚨 CRISIS ZONE: High Exposure"
    hero_title_text = f"You are Pink Slip Proof until Age {display_age_whole_number}"
elif runway_years < 3.0:
    banner_bg = "#7c2d12"       
    banner_border = "#f97316"   
    banner_text = "#fff7ed"     
    status_label = "⚠️ WARNING ZONE: Limited Armor"
    hero_title_text = f"You are Pink Slip Proof until Age {display_age_whole_number}"
else:
    banner_bg = "#064e3b"       
    banner_border = "#10b981"   
    banner_text = "#ecfdf5"     
    status_label = "🟢 SAFETY POOL: Uncompromised Lifestyle Secure"
    hero_title_text = f"You are Pink Slip Proof until Age {display_age_whole_number}"

st.markdown(f"""
    <div class="hero-banner" style="background-color: {banner_bg}; border-color: {banner_border}; color: {banner_text};">
        <div class="hero-subtitle">{status_label}</div>
        <div class="hero-title">{hero_title_text}</div>
    </div>
""", unsafe_allow_html=True)


# --- TWO-CARD METRIC GRID COMPRESSION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pink Slip Runway</div>
            <div class="metric-value">{runway_months:,.0f} <span style="font-size: 1.1rem; color: #94a3b8;">Mos</span> <span style="font-size: 1.5rem; color: #38bdf8; font-weight:700;">({runway_years:.1f} Yrs)</span></div>
            <div class="metric-sub">Portfolio gain - inflation 6%</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Retirement Lockdown</div>
            <div class="metric-value">Life Secured until Age {int(max_safe_age)}</div>
            <div class="metric-sub">The exact milestone your total estate assets completely run out</div>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# ADJUSTED PORTFOLIO BASELINE GRID
# ==========================================
st.write("")
st.write("")
st.subheader("🔄 What Your Balance Sheet Looks Like Now")

disp_equity = st.session_state.equity_base * (1 + (equity_shift / 100))
disp_metals = st.session_state.metals_base * (1 + (metals_shift / 100))

df_portfolio = pd.DataFrame({
    "Asset Class / Liability": ["Stocks & Mutual Funds", "Fixed Income & Deposits", "Gold & Silver", "Remaining Home Value", "⚠️ Outstanding Loans (Debt)"],
    "Your Baseline (₹)": [st.session_state.equity_base, st.session_state.debt_base, st.session_state.metals_base, st.session_state.real_estate_base, total_debts],
    "Simulated Change (₹)": [disp_equity - st.session_state.equity_base, 0, disp_metals - st.session_state.metals_base, -re_liquidation, 0],
    "Active Reality Value (₹)": [disp_equity, sim_debt if runway_months > 0 else 0, disp_metals, adj_home_value, total_debts]
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
        <p style="color: #94a3b8; font-size: 0.95rem;">Join the private vault. We track your assets against real-world market closes, factor in active inflation spikes, and deliver your updated survival timelines every Sunday night.</p>
    </div>
""", unsafe_allow_html=True)

col_sub1, col_sub2, col_sub3 = st.columns([1, 2, 1])
with col_sub2:
    with st.form("subscription_form"):
        email = st.text_input("Enter your secure email to request an invite:")
        submit = st.form_submit_button("Request Private Access")
        if submit and email:
            st.success("Access requested. Welcome to the vault.")
