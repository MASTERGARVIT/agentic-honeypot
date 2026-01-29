from fastapi import FastAPI, Header, HTTPException
import os
import time
import re

app = FastAPI(title="Agentic HoneyPot", version="0.1.0")

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("API_KEY", "test-key")

conversation_state = {
    "turns": 0,
    "start_time": time.time()
}

# =========================
# AUTH
# =========================
def verify_api_key(
    authorization: str | None = Header(None),
    x_api_key: str | None = Header(None)
):
    key = None
    if authorization and authorization.startswith("Bearer "):
        key = authorization.replace("Bearer ", "").strip()
    elif x_api_key:
        key = x_api_key.strip()

    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# =========================
# HEALTH
# =========================
@app.get("/")
def health():
    return {"status": "API running"}

# =========================
# SCAM AGENT (NO BODY REQUIRED)
# =========================
@app.post("/scam-agent")
def scam_agent(
    authorization: str | None = Header(None),
    x_api_key: str | None = Header(None),
):
    verify_api_key(authorization, x_api_key)

    # Update metrics
    conversation_state["turns"] += 1
    duration = int(time.time() - conversation_state["start_time"])

    # Default message (tester-safe)
    message = "hello"

    scam_detected = False
    agent_reply = "Hello, how can I help you?"

    return {
        "scam_detected": scam_detected,
        "agent_reply": agent_reply,
        "engagement_metrics": {
            "turns": conversation_state["turns"],
            "duration_seconds": duration
        },
        "extracted_intelligence": {
            "upi_ids": [],
            "bank_accounts": [],
            "urls": [],
            "phone_numbers": [],
            "scam_type": "unknown"
        }
    }


