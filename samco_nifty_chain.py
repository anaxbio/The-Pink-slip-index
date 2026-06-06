import os, sys, time, requests, warnings, gspread
from datetime import datetime, timedelta, timezone, time as datetime_time
from oauth2client.service_account import ServiceAccountCredentials
warnings.filterwarnings("ignore")



def get_action_tag(ltp_diff, oi_diff):
    if abs(ltp_diff) < 0.25 and abs(oi_diff) < 100: return "Neutral ➖"
    if ltp_diff > 0 and oi_diff > 0: return "Long Buildup 🟢"
    if ltp_diff < 0 and oi_diff > 0: return "Short Buildup 🧱"
    if ltp_diff > 0 and oi_diff < 0: return "Short Covering 🚨"
    if ltp_diff < 0 and oi_diff < 0: return "Long Unwinding 📉"
    return "Neutral ➖"

def fetch_and_calculate(session_token, anchor_state, rolling_history):
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "x-session-token": session_token})
    spot = float(session.get(f"{SAMCO_BASE_URL}/quote/indexQuote?indexName=NIFTY%2050").json()["indexDetails"][0]["spotPrice"])
    atm = int(round(spot / 50.0)) * 50
    expiry = sorted(list(set([l.get("expiryDate") for l in session.get(f"{SAMCO_BASE_URL}/option/optionChain?searchSymbolName=NIFTY&exchange=NFO&strikePrice={atm}").json().get("optionChainDetails", [])])))[0]
    grid, current_state = [], {}
    for sp in [atm + (i * 50) for i in range(-7, 8)]:
        legs = [l for l in session.get(f"{SAMCO_BASE_URL}/option/optionChain?searchSymbolName=NIFTY&exchange=NFO&strikePrice={sp}").json().get("optionChainDetails", []) if l.get("expiryDate") == expiry]
        ce, pe = next((l for l in legs if l["optionType"] == "CE"), {}), next((l for l in legs if l["optionType"] == "PE"), {})
        current_state[sp] = {"ce_ltp": float(ce.get("lastTradedPrice", 0)), "pe_ltp": float(pe.get("lastTradedPrice", 0)), "ce_oi": int(ce.get("openInterest", 0)), "pe_oi": int(pe.get("openInterest", 0)), "ce_chg": float(ce.get("openInterestChange", 0)), "pe_chg": float(pe.get("openInterestChange", 0))}
        time.sleep(0.05)
    if not anchor_state: anchor_state.update(current_state)
    compare_3m = rolling_history[0] if rolling_history else anchor_state 
    for sp, curr in current_state.items():
        anch, comp = anchor_state.get(sp, curr), compare_3m.get(sp, curr)
        ce_day, pe_day = get_action_tag(curr["ce_ltp"] - anch["ce_ltp"], curr["ce_oi"] - anch["ce_oi"]), get_action_tag(curr["pe_ltp"] - anch["pe_ltp"], curr["pe_oi"] - anch["pe_oi"])
        ce_3m, pe_3m = get_action_tag(curr["ce_ltp"] - comp["ce_ltp"], curr["ce_oi"] - comp["ce_oi"]), get_action_tag(curr["pe_ltp"] - comp["pe_ltp"], curr["pe_oi"] - comp["pe_oi"])
        grid.append({"sp": sp, "ce_oi": curr["ce_oi"], "pe_oi": curr["pe_oi"], "ce_ltp": curr["ce_ltp"], "pe_ltp": curr["pe_ltp"], "ce_chg": curr["ce_chg"], "pe_chg": curr["pe_chg"], "ce_day": ce_day, "pe_day": pe_day, "ce_3m": ce_3m, "pe_3m": pe_3m})
    rolling_history.append(current_state)
    if len(rolling_history) > 3: rolling_history.pop(0) 
    top_ce = sorted(grid, key=lambda x: x["ce_oi"], reverse=True)[:2]
    top_pe = sorted(grid, key=lambda x: x["pe_oi"], reverse=True)[:2]
    avg_chg = sum(abs(r["ce_chg"] + r["pe_chg"]) for r in grid) / len(grid)
    total_ce_oi, total_pe_oi = sum(r["ce_oi"] for r in grid), sum(r["pe_oi"] for r in grid)
    ntm_pcr = round(total_pe_oi / total_ce_oi, 2) if total_ce_oi > 0 else 0
    ist_now_str = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S")
    table = [[f"🕒 {ist_now_str} IST", f"📅 {expiry}", f"🎯 NIFTY: {spot}", f"⚖️ NTM PCR: {ntm_pcr}"] + [""] * 10, ["" for _ in range(14)], ["Strike", "SNAP", "WALL", "CE 3-MIN", "CE DAY", "CE LTP", "PE 3-MIN", "PE DAY", "PE LTP", "Straddle", "CE OI", "PE OI", "CE-PE Imb", "Chg COI"]]
    for r in grid:
        chg_coi = r["ce_chg"] + r["pe_chg"]
        is_ce, is_pe = r["sp"] in [x["sp"] for x in top_ce], r["sp"] in [x["sp"] for x in top_pe]
        wall_tag = "🚨 CE & PE WALL" if is_ce and is_pe else ("🚨 CE WALL" if is_ce else ("🚨 PE WALL" if is_pe else ""))
        snap_tag = "🔥 SNAP" if abs(chg_coi) > (avg_chg * 2) and avg_chg > 500 else ""
        table.append([f"{r['sp']} 🎯" if r["sp"] == atm else r["sp"], snap_tag, wall_tag, r["ce_3m"], r["ce_day"], r["ce_ltp"], r["pe_3m"], r["pe_day"], r["pe_ltp"], round(r["ce_ltp"] + r["pe_ltp"], 2) if abs(r["sp"] - atm) <= 100 else "", r["ce_oi"], r["pe_oi"], r["ce_oi"] - r["pe_oi"], chg_coi])
    return table

def execute():
    os.chdir('/home/ubuntu')
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDS_DICT, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open_by_key(SPREADSHEET_ID).worksheet("NIFTY_CHAIN")
    anchor_state, rolling_history = {}, []
    while True:
        try:
            token = open(SESSION_TOKEN_FILE).read().strip()
            data = fetch_and_calculate(token, anchor_state, rolling_history)
            sheet.clear(); sheet.update(range_name='A1', values=data)
            time.sleep(60)
        except Exception as e: time.sleep(10)

if __name__ == "__main__": execute()
