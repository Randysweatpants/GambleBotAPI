# main.py
import os
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="EV Parlay Service", version="1.0.0")

# === Auth (header key set in Render Settings → Environment: X_API_KEY) ===
API_KEY = os.getenv("X_API_KEY")  # optional; enforced only if set

def require_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# === Public routes (no auth) ===
@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok", "health": "/healthz", "docs": "/docs"}

@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"ok": True}

# === Protected routes (require X-API-Key if configured) ===
@app.get("/odds")
def get_odds(
    sport: str,
    window_minutes: int = 240,
    books: Optional[List[str]] = None,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    require_key(x_api_key)
    # TODO: replace with real odds fetching + de-vig
    return {"games": []}

@app.post("/ev_parlays")
def ev_parlays(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    require_key(x_api_key)
    # TODO: replace with real EV logic
    return {"parlays": []}

@app.post("/log_result")
def log_result(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    require_key(x_api_key)
    # TODO: persist results for learning
    return {"ok": True}
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description="EV Parlay Service API",
        routes=app.routes,
    )
    # 👇 Tell clients the canonical HTTPS base URL
    schema["servers"] = [{"url": "https://gamblebotapi.onrender.com"}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi  # <-- register override
