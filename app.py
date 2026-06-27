import sqlite3
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

DB_NAME = "trading_dashboard.db"

# Minimal middleware connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)

# --- Define the data structure for incoming price updates ---
class PriceUpdate(BaseModel):
    symbol: str
    ltp: float
    best_bid: float
    bid_qty: int
    best_ask: float
    ask_qty: int

# --- MATCHES LINE 179: index.html expects raw index tuples r[0], r[1] ---
@app.get("/active")
async def get_active():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, position_type, ticker, quantity, entry_price, account FROM active_positions")
    rows = cursor.fetchall()  # Returns raw tuples: (1, 'SGB', 'SGBDEC26', 10, 13550.0, 'Primary')
    conn.close()
    return {"positions": rows}

# --- 1. THE RETRIEVAL SYSTEM (Replaces Dummy Data) ---
# MATCHES LINE 169: index.html expects a flat array of objects with .symbol and .ltp
@app.get("/live_prices")
async def get_live_prices():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row # Allows us to fetch as dictionaries
    cursor = conn.cursor()

    # Pulling 100% real data from the database
    cursor.execute("SELECT symbol, ltp, best_bid, bid_qty, best_ask, ask_qty FROM market_prices")
    rows = cursor.fetchall()
    conn.close()

    # Convert sqlite3.Row objects to standard Python dictionaries for the JSON response
    return [dict(row) for row in rows]

# --- 2. THE UPDATE SYSTEM (Feeds the Database) ---
@app.post("/live_prices/update")
async def update_live_prices(prices: List[PriceUpdate]):
    conn = get_db_connection()
    cursor = conn.cursor()

    # UPSERT Logic: Insert new row, or update existing row if the symbol already exists
    for p in prices:
        cursor.execute("""
            INSERT INTO market_prices (symbol, ltp, best_bid, bid_qty, best_ask, ask_qty)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                ltp=excluded.ltp,
                best_bid=excluded.best_bid,
                bid_qty=excluded.bid_qty,
                best_ask=excluded.best_ask,
                ask_qty=excluded.ask_qty,
                last_updated=CURRENT_TIMESTAMP
        """, (p.symbol, p.ltp, p.best_bid, p.bid_qty, p.best_ask, p.ask_qty))

    conn.commit()
    conn.close()
    return {"status": "success", "updated_count": len(prices)}

@app.post("/trade/close")
async def close_trade(pos_id: int, exit_price: float, realized_pnl: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_positions WHERE id = ?", (pos_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
