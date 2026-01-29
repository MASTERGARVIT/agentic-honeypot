from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import time
import re

app = FastAPI(title="Agentic HoneyPot", version="0.1.0")

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("API_KEY", "test-key")

# In-memory conversation store (OK for hackathon)
conversation_state = {
    "turns": 0,
    "start_time": time.time()
}

# =========================
# MODELS
# =========================
class ScamRequest(BaseModel):
    message: str

# =========================
# AUTH HANDLER (PATCHED)
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
# HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {"status": "API running"}

# =========================
# SCAM AGENT ENDPOINT
# =========================
@app.post("/scam-agent")
def scam_agent(
    request: ScamRequest,
    authorization: str | None = Header(None),
    x_api_key: str | None = Header(None)
):
    # Auth
    verify_api_key(authorization, x_api_key)

    # Update conversation metrics
    conversation_state["turns"] += 1
    duration = int(time.time() - conversation_state["start_time"])

    message = request.message.lower()

    # Simple scam detection rules
    scam_keywords = ["bank", "blocked", "urgent", "click", "verify", "account"]
    scam_detected = any(word in message for word in scam_keywords)

    # Agent response (keeps scammer engaged)
    agent_reply = (
        "I am a bit confused, can you explain again?"
        if scam_detected
        else "Can you provide more details?"
    )

    # Intelligence extraction (basic but valid)
    urls = re.findall(r"https?://\S+", request.message)
    phone_numbers = re.findall(r"\b\d{10}\b", request.message)

    response = {
        "scam_detected": scam_detected,
        "agent_reply": agent_reply,
        "engagement_metrics": {
            "turns": conversation_state["turns"],
            "duration_seconds": duration
        },
        "extracted_intelligence": {
            "upi_ids": [],
            "bank_accounts": [],
            "urls": urls,
            "phone_numbers": phone_numbers,
            "scam_type": "bank_impersonation" if scam_detected else "unknown"
        }
    }

    return response

