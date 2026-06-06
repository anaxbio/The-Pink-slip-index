import time
from datetime import datetime, timedelta, timezone
import json
import os
import urllib.parse
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import pandas as pd
import pandas_ta as ta
import requests

# ---------------------------------------------------------------------------
# GLOBAL CREDENTIALS & SERVICE CONFIGURATIONS
# ---------------------------------------------------------------------------
USER_ID = "DB34963"
PASSWORD = "Visa1980-"
SECRET_API_KEY = "DB34963_54cgTrvxIHXC6Kj3TBoyR7grGJ194oq-tEVImH4"

SPREADSHEET_ID = "1szR3RP0QO4L_q4liyIptyyrPsm9e39wC2o85Nq38dUM"

GOOGLE_CREDS_DICT = {
    "type": "service_account",
    "project_id": "epmonitor-488507",
    "private_key_id": "8d8438fff6af42862aa78eddd295e3cd92cde7aa",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCzP8y9mWLFwBUt
MxWRMn27NcFqT3tAWa+o71qdc3vzHW9oojDTFU9xGUvToyoix4fDBnkfV5bHNPPm
JbyvF31+U2vXApDCWzhMMgMOZ/sGz4mWNSYjlxiOpnC72NEfJrc2W1dj0Ysn69FP
aBlq1/a94L+cGGMCUDzZkljVXTJaNmVxhsCXr91XtATkrQ6DLDexWGM+wUlhNnxF
51244hvbRGH5SGw+a9z/TLRs0WctzZEjzXg5o1rjDi5TJ1/fSnOhW82qSYkJIIkV
tDGKbMD+Au/wfwfgRZml75zw4LgJ9xpMw+df4NdyOoHnGYQZ+x1xH2TB1jpBUqPJ
sE2gbU71AgMBAAECggEABN6+SYYQWL6zFJfnUk5kru0/99gSL8zMzzJpn0Hsls3K
IbXYAI3H3pL8X2yqD89yBD3gLpZq1bckZUov/TKn/M9En88SPDJnevjk4l0eEePm
1HqIzCPzAKhlabhZvjBUGMyUhduP0O7asGVr3PfiXIUg6TUBNtl6CpASWWgZBSBn
lT/l1gLCqgz7AK9doWhJJYhBxjSERuDIIBnJui4sL+UVqrEjvBbQWhQQnIztFC3I
m1V4KtF1+hAQgVpNkQlNez7VB1SQoQ4stE1UF+G80cOn4YJQyuI+71quUx6tqgQR
MH15SRO+lugWI3n+BVpW10lG/1sPy43s6ZM7uqTChQKBgQDZy+ennb+mhxaOYbyZ
iWOmuL9uOYb87hONUK66HFnWRoF1nrCiS0eNiOgXRKbwdqSAlJUAIWxv/6TSvCYm
RyTmxaW36kZXcdKGAxG7KfWJluW0NqNokunJahRHxDEdwV0mD2HC2JxMQxFlvIRO
aMdCI+VjrnUZh8zmvT62jEc4owKBgQDSsPBnDrpuxO80McyODaot956MhKdo3Bw0
VI3rpUm8WwqG8M4EB4k7dwXxD1TB1ePMKiq1wpR8IzYmnzLWfJ5qpeVCnLtXqKv8
raUFr+F6W2Z+Lq/1ZI7SKQyT2+LCS82RPqO0xGyICutPeCwKgtPYxILpx6kiw5Gw
0ETGoJnbhwKBgQDZD+NcpldvfIr6dGYnD0qFyvLew+7I/e32lUbOrZrLd5FmzDV2
SliRsrS9G+rVFSl2DJ9DdgxAwyRd8q6Cz7zzUmCLH63jUMlkToLJalQQQJfGN/48
Js9hsZtsuxfIdAKGACaKrp93UhBwuKWUD9EnFed0pVaHj1SjUlDCVqRUyQKBgFMo
iUpz8rvDuRIl0bIDzLal9ItL1HO75Nn2walPrOHOIUKPixDmFJFG8i5qOa7kCCxO
PFtPOKIil734ue0UdMZtQibfi8YWigOKWgb7m4hayQJm1QaLMR/cGd3GPSMpHjME
wUKZAKlVffj42pEvgAQf0/gH2UciX7+lBHBNdUzDAoGASmvegL4StGPDeYmU8azo
TWNSNknWwOayKaECP73atu+K3IEO4e1YvSrFNCICMYjxfYY2edoXR1JMaN+jrAla
h7sg0PVK6RHKj9HXo/902b43Pa4PgQeNOQLk8YkbvujyUfSgptRyXsoG5S6H3E3H
tmKvcKypfbZwXzmfkF6sb2Y=
-----END PRIVATE KEY-----
""",
    "client_email": "trader-bot@epmonitor-488507.iam.gserviceaccount.com",
    "client_id": "103607271622108574925",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/raw/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/trader-bot%40epmonitor-488507.iam.gserviceaccount.com"
}

SESSION_TOKEN_FILE = "/home/ubuntu/samco_session.txt"
SCRIP_CACHE_FILE = "/home/ubuntu/samco_master_cache.json"
SAMCO_BASE_URL = "https://tradeapi.samco.in"


def clean_float(val):
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    try: return float(str(val).replace(",", "").strip())
    except: return 0.0


def load_or_refresh_session():
    if os.path.exists(SESSION_TOKEN_FILE):
        file_time = datetime.fromtimestamp(os.path.getmtime(SESSION_TOKEN_FILE))
        if file_time.date() == datetime.today().date() and file_time.hour >= 8:
            with open(SESSION_TOKEN_FILE, "r") as f:
                token = f.read().strip()
                if token: return token

    print("[*] Access token expired or missing. Triggering Samco authentication...")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        r1 = requests.post(f"{SAMCO_BASE_URL}/accessToken/token", json={"uid": USER_ID, "secretApiKey": SECRET_API_KEY}, headers=headers, timeout=15)
        if r1.status_code == 200 and r1.json().get("status") == "Success":
            access_token = r1.json().get("accessToken")
            r2 = requests.post(f"{SAMCO_BASE_URL}/login", json={"userId": USER_ID, "password": PASSWORD, "accessToken": access_token}, headers=headers, timeout=15)
            if r2.status_code == 200 and r2.json().get("status") == "Success":
                session_token = r2.json().get("sessionToken")
                with open(SESSION_TOKEN_FILE, "w") as f:
                    f.write(session_token)
                print("[+] Samco master connection established and absolute token dropped.")
                return session_token
    except Exception as e:
        print(f"[-] Critical Samco Handshake Error: {e}")
    return None


def fetch_samco_quote(session_token, symbol, exchange="NSE"):
    encoded_sym = urllib.parse.quote(symbol.strip())
    headers = {"Accept": "application/json", "x-session-token": session_token}
    
    if "NIFTY" in symbol.upper():
        url = f"{SAMCO_BASE_URL}/quote/indexQuote?indexName={encoded_sym}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "Success":
                    details = data.get("indexDetails", [])
                    if details:
                        return {"lastTradedPrice": details[0].get("spotPrice", 0.0)}
        except: pass
    else:
        url = f"{SAMCO_BASE_URL}/quote/getQuote?symbolName={encoded_sym}&exchange={exchange.upper()}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "Success" and "quoteDetails" in data:
                    return data["quoteDetails"]
        except: pass
    return None


def fetch_historical_candles(session_token, symbol, exchange="NSE", interval="15", days_back=7):
    encoded_sym = urllib.parse.quote(symbol.strip())
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    url = (
        f"{SAMCO_BASE_URL}/historical/candleData?"
        f"symbolName={encoded_sym}&exchange={exchange.upper()}&"
        f"fromDate={start_date.strftime('%Y-%m-%d')}&toDate={end_date.strftime('%Y-%m-%d')}&"
        f"interval={interval}"
    )
    headers = {"Accept": "application/json", "x-session-token": session_token}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if "candleData" in data:
                df = pd.DataFrame(data["candleData"])
                df['close'] = pd.to_numeric(df['close'].astype(str).str.replace(',', ''), errors='coerce')
                df['high'] = pd.to_numeric(df['high'].astype(str).str.replace(',', ''), errors='coerce')
                df['low'] = pd.to_numeric(df['low'].astype(str).str.replace(',', ''), errors='coerce')
                return df
    except: pass
    return pd.DataFrame()


def compute_local_silent_signal(df):
    if df.empty or len(df) < 20:
        return {"Trend": 1, "TrailSL": 0.0, "Signal": "WAIT/CHOP"}
    try:
        df['EMA200'] = ta.ema(df['close'], length=200)
        df.ta.adx(append=True)
        adx_col = [c for c in df.columns if c.startswith('ADX')][0]
        df['ADX'] = df[adx_col]

        atr = ta.atr(df['high'], df['low'], df['close'], length=10)
        hl2 = (df['high'] + df['low']) / 2
        df['Up'] = hl2 - (3 * atr)
        df['Dn'] = hl2 + (3 * atr)

        closes, ups, dns = df['close'].to_numpy(), df['Up'].to_numpy(), df['Dn'].to_numpy()
        tup, tdown, trend = np.zeros(len(df)), np.zeros(len(df)), np.ones(len(df))

        for i in range(1, len(df)):
            tup[i] = max(ups[i], tup[i-1]) if closes[i-1] > tup[i-1] else ups[i]
            tdown[i] = min(dns[i], tdown[i-1]) if closes[i-1] < tdown[i-1] else dns[i]
            if closes[i] > tdown[i-1]: trend[i] = 1
            elif closes[i] < tup[i-1]: trend[i] = -1
            else: trend[i] = trend[i-1]

        df['Trend'] = trend
        df['TrailSL'] = np.where(df['Trend'] == 1, tup, tdown)

        last, prev = df.iloc[-1], df.iloc[-2]
        is_trending = last['ADX'] > 20
        is_aligned = (last['Trend'] == 1 and last['close'] > last['EMA200']) or (last['Trend'] == -1 and last['close'] < last['EMA200'])

        signal = "WAIT/CHOP"
        if last['Trend'] == 1 and prev['Trend'] == -1 and is_trending and is_aligned: signal = "🟢 NEW BUY"
        elif last['Trend'] == -1 and prev['Trend'] == 1 and is_trending and is_aligned: signal = "🔴 NEW SELL"
        elif last['Trend'] == 1: signal = "⏳ HOLD LONG"
        elif last['Trend'] == -1: signal = "⏳ HOLD SHORT"

        return {"Trend": int(last['Trend']), "TrailSL": round(float(last['TrailSL']), 2), "Signal": signal}
    except:
        return {"Trend": 1, "TrailSL": 0.0, "Signal": "ERROR"}


def fetch_samco_master_scrips():
    """OPTIMIZATION: Downloads Samco Master File EXACTLY ONCE on startup.
    Uses local backup file cache if Samco rate-limits the network request."""
    print("[*] Pulling Samco Master Database (1 Time Per Day Target)...")
    discovered = set()
    url = "https://developers.stocknote.com/doc/ScripMaster.csv"
    try:
        res = requests.get(url, timeout=45)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                line_upper = line.upper().strip()
                if "MCX" in line_upper:
                    gold_matches = re.findall(r'(GOLDPETAL[A-Z0-9]*FUT)', line_upper)
                    for m in gold_matches: discovered.add((m, "MCX"))
                    silver_matches = re.findall(r'(SILVERMIC[A-Z0-9]*FUT)', line_upper)
                    for m in silver_matches: discovered.add((m, "MCX"))
                
                sgb_matches = re.findall(r'\b(SGB[A-Z0-9]+)', line_upper)
                for m in sgb_matches:
                    if len(m) >= 7: discovered.add((m, "NSE"))
            
            # Save a copy to local disk drive to withstand network drops
            with open(SCRIP_CACHE_FILE, "w") as f:
                json.dump([list(item) for item in discovered], f)
            print(f"[+] Master file parsed successfully. Cached {len(discovered)} global assets.")
            return discovered
    except Exception as e:
        print(f"[!] Samco endpoint connection failed/throttled: {e}")
        
    # Failover local cache routine
    if os.path.exists(SCRIP_CACHE_FILE):
        print("[*] Activating local backup cache failover...")
        try:
            with open(SCRIP_CACHE_FILE, "r") as f:
                loaded = json.load(f)
                discovered = set((item[0], item[1]) for item in loaded)
                print(f"[+] Loaded {len(discovered)} contracts seamlessly from local storage matrix.")
                return discovered
        except Exception as cache_err:
            print(f"[-] Local file parse crash: {cache_err}")
            
    return discovered


def discover_master_universe(workbook, cached_master_scrips):
    """Combines the pre-fetched global scrips with fresh spreadsheet tab watchlists."""
    print("[*] Synchronizing workspace configurations from Google Sheets...")
    discovered_universe = set(cached_master_scrips)
    watchlist_symbols = set()

    static_desks = [
        ("silver_etfs", "Silver ETF", "NSE"),   
        ("MASTER_WATCHLIST", "Symbol", "NSE"),
        ("mcx_shorts", "Contract", "MCX")
    ]
    for ws_name, col_name, fixed_exch in static_desks:
        try:
            ws = workbook.worksheet(ws_name)
            for r in ws.get_all_records():
                sym = str(r.get(col_name, "")).strip()
                sym_up = sym.upper()
                if sym and sym_up not in ["GOLDPETAL", "SILVERMIC", "SGB"]:
                    if "NIFTY" in sym_up:
                        discovered_universe.add((sym, "NSE"))
                        if ws_name == "MASTER_WATCHLIST": watchlist_symbols.add(sym)
                    else:
                        discovered_universe.add((sym, fixed_exch))
                        if ws_name == "MASTER_WATCHLIST": watchlist_symbols.add(sym)
        except: pass

    baseline_etfs = {
        ("GOLDBEES", "NSE"), ("SILVERBEES", "NSE"), 
        ("GOLDBEINAV", "NSE"), ("SILVERINAV", "NSE"), 
        ("GOLDCASE", "NSE"), ("SILVERCASE", "NSE")
    }
    discovered_universe.update(baseline_etfs)

    sorted_universe = sorted(list(discovered_universe), key=lambda x: (x[1], x[0]))
    print(f"[+] Target calculations refreshed. {len(sorted_universe)} items loaded. {len(watchlist_symbols)} on active TA monitor.")
    return sorted_universe, watchlist_symbols


def execute_relay_pipeline():
    print(f"[*] Activating Core Pipeline Sequence...")
    session_token = load_or_refresh_session()
    if not session_token: return

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDS_DICT, scope)
        gc = gspread.authorize(creds)
        workbook = gc.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        print(f"[-] Google initialization failure: {e}")
        return

    # PHASE 1 FIXED: Pull the massive Samco file EXACTLY ONCE on boot
    cached_master_scrips = fetch_samco_master_scrips()
    
    # Initialize complete portfolio lists from workspace tabs
    master_universe, watchlist_symbols = discover_master_universe(workbook, cached_master_scrips)
    last_discovery_time = datetime.now()

    while True:
        now = datetime.now()
        if now.hour == 23 and now.minute >= 30:
            print("[+] Market boundaries closed. Disengaging harvester.")
            break

        # Refresh from Google Sheets tabs every 30 mins, bypassing Samco network spam entirely
        if datetime.now() - last_discovery_time >= timedelta(minutes=30):
            print("[*] 30-minute boundary reached. Checking spreadsheet tabs for updates...")
            try:
                master_universe, watchlist_symbols = discover_master_universe(workbook, cached_master_scrips)
                last_discovery_time = datetime.now()
            except Exception as e:
                print(f"[-] Throttled workspace refresh failed, continuing with active list: {e}")

        try:
            live_data_cache = {}
            for symbol, exch in master_universe:
                quote = fetch_samco_quote(session_token, symbol, exch)
                ltp, bid, ask = 0.0, 0.0, 0.0
                
                if quote:
                    ltp = clean_float(quote.get("lastTradedPrice", 0.0))
                    bids = quote.get("bestBids", [])
                    if bids and len(bids) > 0: bid = clean_float(bids[0].get("price", 0.0))
                    asks = quote.get("bestAsks", [])
                    if asks and len(asks) > 0: ask = clean_float(asks[0].get("price", 0.0))
                
                trend_val, trail_sl, signal_str = "", "", ""
                
                if symbol in watchlist_symbols:
                    trend_val, trail_sl, signal_str = 1, 0.0, "⏳ HOLD LONG"
                    candles = fetch_historical_candles(session_token, symbol, exch, interval="15", days_back=7)
                    if not candles.empty:
                        math_res = compute_local_silent_signal(candles)
                        trend_val = math_res["Trend"]
                        trail_sl = math_res["TrailSL"]
                        signal_str = math_res["Signal"]

                live_data_cache[symbol] = {
                    "LTP": ltp, "Best_Bid": bid, "Best_Ask": ask,
                    "Trend": trend_val, "StopLoss": trail_sl, "Signal": signal_str,
                    "Timestamp": (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
                }

            try:
                output_sheet = workbook.worksheet("LIVE_PRICES")
                header_row = ["Symbol", "LTP", "Best_Bid", "Best_Ask", "Trend", "StopLoss", "Signal", "Timestamp"]
                summary_matrix = []
                for s in live_data_cache:
                    c = live_data_cache[s]
                    summary_matrix.append([s, c["LTP"], c["Best_Bid"], c["Best_Ask"], c["Trend"], c["StopLoss"], c["Signal"], c["Timestamp"]])
                
                output_sheet.clear()
                output_sheet.update(range_name='A1', values=[header_row] + summary_matrix, value_input_option='USER_ENTERED')
                print(f"[+++] Dynamic Cloud Canvas Flushed Successfully. Rows: {len(summary_matrix)}. Sleeping for 60s...")
            except Exception as e:
                print(f"[-] Summary tab flush error: {e}")

        except Exception as e:
            print(f"[-] Harvester cycle runtime error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    execute_relay_pipeline()
