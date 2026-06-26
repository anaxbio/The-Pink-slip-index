import os
import asyncio
import sqlite3
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from contextlib import asynccontextmanager

# --- STRICT IN-MEMORY CACHE ---
live_market_cache = []

async def fetch_live_prices_background():
    """
    Raw execution loop. 
    Insert your actual Google Sheets/API fetch logic here. 
    No try/except fallbacks. If it throws an error, the task dies.
    """
    while True:
        # EXECUTE YOUR REAL FETCH HERE
        # Example: 
        # raw_data = your_gsheets_client.get_all_records()
        # live_market_cache.clear()
        # live_market_cache.extend(raw_data)
        
        await asyncio.sleep(15)

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(fetch_live_prices_background())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

# --- CONFIG & SECURITY ---
DB_NAME = "trading_dashboard.db"
API_KEY = os.getenv("ZONE4_API_KEY") 

async def verify_key(x_api_key: str = Header(...)):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

class NewTrade(BaseModel):
    position_type: str
    ticker: str
    quantity: float
    entry_price: float
    account: str

# --- THE FIREHOSE ENDPOINT ---
@app.get("/live_prices", dependencies=[Depends(verify_key)])
async def get_live_prices():
    # Returns exactly what is in the cache, nothing else.
    return live_market_cache

# --- EXISTING ENDPOINTS ---
@app.get("/active", dependencies=[Depends(verify_key)])
async def get_active():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM active_positions")
    rows = cursor.fetchall()
    conn.close()
    return {"positions": rows}

@app.get("/closed", dependencies=[Depends(verify_key)])
async def get_closed():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM closed_metals")
    rows = cursor.fetchall()
    conn.close()
    return {"history": rows}

@app.post("/positions/add", dependencies=[Depends(verify_key)])
async def add_position(trade: NewTrade):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO active_positions (position_type, ticker, quantity, entry_price, account) VALUES (?, ?, ?, ?, ?)",
        (trade.position_type, trade.ticker, trade.quantity, trade.entry_price, trade.account)
    )
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/trade/close", dependencies=[Depends(verify_key)])
async def close_trade(pos_id: int, exit_price: float, realized_pnl: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM active_positions WHERE id = ?", (pos_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Logic to move to closed_metals goes here
    
    conn.close()
    return {"status": "closed"}
