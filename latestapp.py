import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# NEW: Import the premium business logic router using the absolute path from the project root
from api.router_premium import router as premium_router 

# Load structural configurations from the root .env file into server RAM
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(
    title="PinkSlipIndex Premium Math Engine",
    version="2.0.0",
    docs_url=None,       # Production Hardening: Disable Swagger UI
    redoc_url=None       # Production Hardening: Disable ReDoc UI
)

# Phase 5 Checklist Target: Inject FastAPI CORS Middleware
# Allows the static frontend on Cloudflare Pages to securely connect to this ARM backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pinkslipindex.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Mount the premium business logic router to the main application
app.include_router(premium_router)

@app.get("/v2/health")
def health_check():
    """Stateless health indicator to verify the engine is live in RAM."""
    return {
        "status": "healthy",
        "engine": "stateless_premium_math",
        "environment": os.getenv("API_ENV", "staging")
    }
