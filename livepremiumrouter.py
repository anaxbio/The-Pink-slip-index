import os
import time
import jwt
import requests
import razorpay
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel

router = APIRouter()

# --- INJECTED PYDANTIC VALIDATION SCHEMA ---
class VaultFlatPayload(BaseModel):
    current_age: float
    inflation_slider: float
    panic_toggle: bool

    inc_salary: float
    inc_business: float
    inc_consulting: float
    inc_rental: float

    exp_rent_emi: float
    exp_other_emi: float
    exp_food_kirana: float
    exp_utilities: float
    exp_domestic_help: float
    exp_fuel_commute: float
    exp_dining_out: float
    exp_other_1: float
    exp_other_2: float
    exp_misc_buffer: float

    ann_insurance: float
    ann_school_fees: float
    ann_festivals: float
    ann_maintenance: float
    ann_vacations: float

    ast_demat: float
    ast_mf_eq: float
    ast_pe: float
    ast_fd: float
    ast_mf_debt: float
    ast_bonds: float
    ast_nps: float
    ast_cash: float
    ast_gold_digi: float
    ast_re_primary: float
    ast_re_second: float
    ast_gold_phys: float

    lia_home_primary: float
    lia_home_second: float
    lia_auto: float
    lia_personal: float
    lia_education: float
    lia_cc: float
    lia_other: float

    stcg_equity: float
    re_taxable_gain: float
    re_distress_pct: float

    equity_shift: float
    metals_shift: float
    expense_shock: float
    re_liquidation: float
    simulated_monthly_rent: float


# --- CONFIGURATION RETRIEVAL FROM RAM ---
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "2880"))
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "Premium Access <send@pinkslipindex.com>")

# NEW: Razorpay Keys
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# NEW: Initialize Razorpay Client
rzp_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# --- STATELESS AUTHENTICATION DEPENDENCY ---
def verify_premium_token(authorization: str = Header(None)):
    """
    Cryptographically decodes and verifies the incoming JWT token in RAM.
    Bypasses any database lookups entirely.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header.")
    
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token type prefix.")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (ValueError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Access token is invalid or expired.")

# --- NEW: ORDER CREATION ENDPOINT (PHASE 2) ---
class OrderRequest(BaseModel):
    customer_email: str

@router.post("/checkout/create_order")
async def create_razorpay_order(data: OrderRequest):
    """
    Generates a secure Order ID from Razorpay to initialize the frontend checkout modal.
    """
    if not data.customer_email:
        raise HTTPException(status_code=400, detail="Email required")
        
    try:
        # Amount is in paise (99900 = 999 INR)
        order_data = {
            "amount": 99900, 
            "currency": "INR",
            "receipt": "vault_premium_access",
            "notes": {
                "email": data.customer_email
            }
        }
        order = rzp_client.order.create(data=order_data)
        return {"order_id": order["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- WEBHOOK & MAGIC LINK GENERATION ENDPOINTS (PHASE 3) ---
@router.post("/webhook/checkout")
async def payment_gateway_webhook(request: Request):
    """
    Strict Razorpay webhook listener. Verifies cryptographic signature before dispatching Magic Link.
    """
    # 1. Grab raw body and Razorpay signature
    raw_body = await request.body()
    gateway_signature = request.headers.get("X-Razorpay-Signature")

    if not gateway_signature:
        raise HTTPException(status_code=403, detail="Missing Razorpay signature.")
    
    # 2. Cryptographically Verify Signature
    try:
        rzp_client.utility.verify_webhook_signature(
            raw_body.decode('utf-8'), 
            gateway_signature, 
            RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=403, detail="Webhook signature mismatch. Forgery detected.")
    
    # 3. Extract Email from Razorpay Payload
    payload = await request.json()
    try:
        customer_email = payload['payload']['payment']['entity']['email']
    except KeyError:
        raise HTTPException(status_code=420, detail="Missing customer email in Razorpay payload.")
    
    # 4. Mint the 48-Hour Token in RAM
    expiration_epoch = int(time.time()) + (TOKEN_EXPIRY_MINUTES * 60)
    token_claims = {
        "sub": customer_email,
        "exp": expiration_epoch,
        "iat": int(time.time()),
        "scope": "premium_math"
    }
    encoded_jwt = jwt.encode(token_claims, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # 5. Construct the Stateless Magic Link Destination
    magic_link = f"https://pinkslipindex.com/vault.html?token={encoded_jwt}"
    
    # 6. Dispatch via Resend API Client
    resend_url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    email_data = {
        "from": FROM_EMAIL,
        "to": [customer_email],
        "subject": "Your Premium Vault Access Link",
        "html": f"""
        <p>Thank you for your purchase.</p>
        <p>Click the link below to access the Premium Vault engine. This link is valid for 48 hours:</p>
        <p><a href="{magic_link}" style="color: #0070f3; text-decoration: underline;">Access Premium Vault Engine</a></p>
        <p>If you did not make this request, please disregard this email.</p>
        """
    }
    
    try:
        response = requests.post(resend_url, json=email_data, headers=headers)
        if response.status_code not in [200, 201]:
            print(f"Resend dispatch malfunction code: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Mail system failure.")
    except Exception as e:
        print(f"Egress pipeline error contacting Resend: {str(e)}")
        raise HTTPException(status_code=500, detail="Outbound network communication failure.")
        
    return {"status": "dispatched", "recipient": customer_email}

# --- SACRED MATHEMATICAL CALCULATION ENGINE (PROTECTED) ---
@router.post("/v2/vault_calc")
async def process_flat_premium_math(data: VaultFlatPayload, token_payload: dict = Depends(verify_premium_token)):
    """
    Pure mathematical calculations running entirely within server volatility.
    Protected by the stateless verified token dependency wrapper.
    """
    is_panic = data.panic_toggle
    active_inflow = 0.0 if is_panic else (data.inc_salary + data.inc_business + data.inc_consulting)
    total_inflow = active_inflow + data.inc_rental

    raw_monthly_burn = (data.exp_rent_emi + data.exp_other_emi + data.exp_food_kirana + 
                        data.exp_utilities + data.exp_domestic_help + data.exp_fuel_commute + 
                        data.exp_dining_out + data.exp_other_1 + data.exp_other_2 + data.exp_misc_buffer)

    raw_annual_spikes = (data.ann_insurance + data.ann_school_fees + data.ann_festivals + 
                         data.ann_maintenance + data.ann_vacations)

    equity_base = data.ast_demat + data.ast_mf_eq + data.ast_pe
    debt_base = data.ast_fd + data.ast_mf_debt + data.ast_bonds + data.ast_nps
    cash_base = data.ast_cash
    metals_base = data.ast_gold_digi + data.ast_gold_phys
    real_estate_base = data.ast_re_primary + data.ast_re_second

    home_loan_base = data.lia_home_primary + data.lia_home_second
    other_loan_base = data.lia_auto + data.lia_personal + data.lia_education + data.lia_cc + data.lia_other
    total_debts = home_loan_base + other_loan_base

    absolute_expense_shock = raw_monthly_burn * (data.expense_shock / 100)
    base_monthly_outflow = raw_monthly_burn + absolute_expense_shock + (raw_annual_spikes / 12)

    final_equity = equity_base * (1 + (data.equity_shift / 100))
    final_metals = metals_base * (1 + (data.metals_shift / 100))

    if is_panic:
        total_eq_loss = data.stcg_equity * 0.20
        other_loss = debt_base * 0.01
        if data.re_liquidation > 0 and real_estate_base > 0:
            re_loss = (data.re_liquidation * (data.re_distress_pct / 100)) + (data.re_taxable_gain * (data.re_liquidation / real_estate_base) * 0.125)
        else:
            re_loss = 0.0
    else:
        total_eq_loss = max(0.0, final_equity - (equity_base * 0.7)) * 0.125
        re_loss = max(0.0, data.re_liquidation - (data.re_liquidation * 0.6)) * 0.125 if data.re_liquidation > 0 else 0.0
        other_loss = debt_base * 0.05

    total_friction = total_eq_loss + re_loss + other_loss
    effective_re_released = max(0.0, data.re_liquidation - re_loss - home_loan_base)

    sim_eq = final_equity - total_eq_loss
    sim_db = (debt_base - other_loss) + cash_base + effective_re_released
    sim_hd = (real_estate_base - data.re_liquidation) + final_metals

    completed_months = 0
    timeline_burn_rate = base_monthly_outflow
    
    active_simulated_rent = int(round((real_estate_base * 0.03) / 12)) if data.re_liquidation > 0 else 0
    loop_simulated_rent = data.simulated_monthly_rent if data.simulated_monthly_rent > 0 else active_simulated_rent
    current_rental_yield = data.inc_rental

    for m in range(1, 601):
        sim_age = data.current_age + (m / 12)
        sim_eq *= (1 + (0.10 / 12))
        sim_db *= (1 + (0.07 / 12))
        sim_hd *= (1 + (0.05 / 12))

        active_career_inflow = 0.0 if sim_age >= 60 else active_inflow
        if m % 12 == 0:
            current_rental_yield *= 0.98
        real_time_inflow = active_career_inflow + (0.0 if is_panic else current_rental_yield)

        running_monthly_burn = (timeline_burn_rate - (data.exp_rent_emi + data.exp_other_emi)) + loop_simulated_rent

        monthly_deficit = running_monthly_burn - real_time_inflow

        if monthly_deficit > 0:
            if sim_db >= monthly_deficit:
                sim_db -= monthly_deficit
            else:
                short = monthly_deficit - sim_db
                sim_db = 0
                if sim_eq >= short:
                    sim_eq -= short
                else:
                    sim_eq = 0
                    break
        else:
            sim_db += abs(monthly_deficit)

        completed_months += 1
        if m % 12 == 0:
            timeline_burn_rate *= (1 + (data.inflation_slider / 100))
            loop_simulated_rent *= (1 + (data.inflation_slider / 100))

    return {
        "completed_months": completed_months,
        "total_friction": total_friction,
        "total_eq_loss": total_eq_loss,
        "re_loss": re_loss,
        "other_loss": other_loss,
        "effective_re_released": effective_re_released,
        "final_equity": final_equity,
        "final_metals": final_metals,
        "equity_base": equity_base,
        "debt_base": debt_base,
        "cash_base": cash_base,
        "metals_base": metals_base,
        "real_estate_base": real_estate_base,
        "home_loan_base": home_loan_base,
        "total_debts": total_debts,
        "raw_monthly_burn": raw_monthly_burn,
        "raw_annual_spikes": raw_annual_spikes
    }
