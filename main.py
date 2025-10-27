import os
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="EV Parlay Service", version="1.0.0")

API_KEY = os.getenv("X_API_KEY")  # set this in Render → Settings → Environment

def require_key(x_api_key: Optional[str]):
    # If you haven't set X_API_KEY yet, allow all (for first boot). Once set, enforce.
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/odds")
def get_odds(
    sport: str,
    window_minutes: int = 240,
    books: Optional[List[str]] = None,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    require_key(x_api_key)
    # Stub payload; replace with real odds later
    return {"games": []}

@app.post("/ev_parlays")
def ev_parlays(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    require_key(x_api_key)
    # Stub payload; replace with your EV logic
    return {"parlays": []}

@app.post("/log_result")
def log_result(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    require_key(x_api_key)
    return {"ok": True}
