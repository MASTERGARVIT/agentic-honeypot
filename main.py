from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY", "test-key")


# ----------- Request Models (match evaluator) -----------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class Metadata(BaseModel):
    channel: str
    language: str
    locale: str


class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict]
    metadata: Metadata


# ----------- Auth -----------

def verify_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ----------- Health -----------

@app.get("/")
def health():
    return {"status": "API running"}


# ----------- Scam Agent Endpoint -----------

@app.post("/scam-agent")
def scam_agent(
    payload: ScamRequest,
    x_api_key: str = Header(...)
):
    verify_key(x_api_key)

    text = payload.message.text.lower()

    scam_keywords = [
        "blocked",
        "verify",
        "otp",
        "urgent",
        "account",
        "compromised",
        "click",
        "suspended"
    ]

    is_scam = any(word in text for word in scam_keywords)

    if is_scam:
        reply = "Why is my account being suspended?"
    else:
        reply = "Can you explain more clearly?"

    # ✅ EXACT format evaluator expects
    return {
        "status": "success",
        "reply": reply
    }



