import sqlite3
import os
import json
import re
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- CONFIGURATION ---
DB_PATH = "/home/ubuntu/financial_api/dark_vault/momo_vault.db"

async def verify_vault_token(x_vault_token: str = Header(None, alias="X-Vault-Token")):
    """Validates that incoming requests contain the valid pre-shared security token from .env."""
    expected_token = os.getenv("VAULT_ACCESS_KEY")
    if not expected_token:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            expected_token = os.getenv("VAULT_ACCESS_KEY")
        except ImportError:
            pass
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Security Configuration Error: VAULT_ACCESS_KEY is not defined in the server's .env file."
        )
    if not x_vault_token or x_vault_token != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing or invalid secure access token."
        )
    return x_vault_token

router = APIRouter(
    prefix="/api/vault",
    tags=["Momo Vault Gateways"],
    dependencies=[Depends(verify_vault_token)]
)

# --- PYDANTIC SCHEMAS ---
class TradeExecutionSchema(BaseModel):
    strategy: str = Field(..., example="920_STRANGLE")
    symbol: str = Field(..., example="NIFTY_ATM_24000")
    qty: float = Field(..., example=75.0)
    entry_price: float = Field(..., example=180.0)
    exit_price: float = Field(..., example=140.0)
    realized_pnl: float = Field(..., example=3000.0)

class LedgerItemSchema(BaseModel):
    id: Optional[int] = None
    account: str = Field(..., example="SAMCO_PRO")
    owner: str = Field(..., example="Core_Desk")
    asset_name: str = Field(..., example="GOLDBEES")
    isin: Optional[str] = Field(None, example="INF200K01153")
    asset_class: str = Field(..., example="SGB") # SGB, Silver ETF, MCX Gold, MCX Silver
    qty: float = Field(..., example=150.0)
    avg_price: float = Field(..., example=62.50)

class ClosePositionSchema(BaseModel):
    id: int = Field(..., example=1)
    df_type: str = Field(..., example="sgb") # sgb, silv, mcx
    close_qty: float = Field(..., example=10.0)
    exit_price: float = Field(..., example=7500.0)
    realized_pnl: float = Field(..., example=5000.0)

# --- HELPER UTILITIES ---
def safe_float(val: Any) -> float:
    if val is None:
        return 0.0
    try:
        return float(str(val).replace(",", "").strip())
    except ValueError:
        return 0.0

# --- READ ENDPOINTS ---

@router.get("/market_data")
async def get_live_market_data():
    """Fetches the absolute latest tick for each symbol from the SQLite WAL cache without any fallbacks."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file missing.")
    
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol, ltp, bid, ask, volume, open_interest, timestamp 
            FROM live_market_data 
            WHERE id IN (SELECT MAX(id) FROM live_market_data GROUP BY symbol);
        ''')
        rows = cursor.fetchall()
        conn.close()

        results = {}
        for r in rows:
            sym = r[0]
            results[sym] = {
                "ltp": safe_float(r[1]),
                "bid": safe_float(r[2]),
                "ask": safe_float(r[3]),
                "volume": int(r[4] or 0),
                "oi": int(r[5] or 0),
                "timestamp": r[6]
            }
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Read Failure: {str(e)}")

@router.get("/metals_analytics")
async def get_metals_analytics():
    """Extracts raw ledger items for client-side processing."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file missing.")

    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # Pull everything from the database ledger so the frontend can group, filter, and run math
        cursor.execute('''
            SELECT id, account, owner, asset_name, isin, asset_class, qty, avg_price 
            FROM portfolio_ledger;
        ''')
        ledger_items = []
        for r in cursor.fetchall():
            ledger_items.append({
                "id": r[0],
                "account": r[1],
                "owner": r[2],
                "asset_name": r[3],
                "isin": r[4] or "",
                "asset_class": r[5],
                "qty": safe_float(r[6]),
                "avg_price": safe_float(r[7])
            })
        conn.close()

        return {
            "status": "Success",
            "ledger_items": ledger_items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Query Error: {str(e)}")

@router.post("/close_position")
async def close_position(payload: ClosePositionSchema):
    """Executes long/short positions close commands and archives transaction details."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file missing.")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT account, asset_name, qty, avg_price, asset_class, owner 
            FROM portfolio_ledger 
            WHERE id = ?;
        ''', (payload.id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Target position ID not found in database ledger.")

        account, symbol, current_qty, entry_price, asset_class, owner = row
        new_qty = max(0.0, current_qty - payload.close_qty)

        if new_qty <= 0.0:
            cursor.execute("DELETE FROM portfolio_ledger WHERE id = ?;", (payload.id,))
        else:
            cursor.execute('''
                UPDATE portfolio_ledger 
                SET qty = ?, last_updated = CURRENT_TIMESTAMP 
                WHERE id = ?;
            ''', (new_qty, payload.id))

        now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        timestamp = now_ist.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now_ist.strftime("%d-%b-%y")

        cursor.execute('''
            INSERT INTO trade_execution_log (timestamp, date, pan, strategy, symbol, qty, entry_price, exit_price, realized_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (timestamp, date_str, owner, asset_class, symbol, payload.close_qty, entry_price, payload.exit_price, payload.realized_pnl))

        conn.commit()
        conn.close()
        return {"status": "Success", "detail": f"Successfully closed {payload.close_qty} units of {symbol}."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Modification Failure: {str(e)}")

@router.post("/upsert_ledger_item")
async def upsert_ledger_item(payload: LedgerItemSchema):
    """Inserts a new asset entry or modifies an existing holding directly inside SQLite."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file missing.")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        cursor = conn.cursor()

        invested_value = payload.qty * payload.avg_price

        # Check if we are updating an existing row
        if payload.id:
            cursor.execute('''
                UPDATE portfolio_ledger 
                SET account = ?, owner = ?, asset_name = ?, isin = ?, asset_class = ?, qty = ?, avg_price = ?, invested_value = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?;
            ''', (payload.account, payload.owner, payload.asset_name, payload.isin or "", payload.asset_class, payload.qty, payload.avg_price, invested_value, payload.id))
        else:
            cursor.execute('''
                INSERT INTO portfolio_ledger (account, owner, asset_name, isin, asset_class, qty, avg_price, invested_value, current_value, unrealized_pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0);
            ''', (payload.account, payload.owner, payload.asset_name, payload.isin or "", payload.asset_class, payload.qty, payload.avg_price, invested_value, invested_value))

        conn.commit()
        conn.close()
        return {"status": "Success", "detail": "Portfolio Ledger updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Update Failure: {str(e)}")
