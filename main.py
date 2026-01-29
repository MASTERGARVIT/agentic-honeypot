from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import time
import re
import os
from openai import OpenAI

load_dotenv()
app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# In-memory stores
# -----------------------------
conversations = {}
intelligence_store = {}

# -----------------------------
# Request schema
# -----------------------------
class ScamRequest(BaseModel):
    conversation_id: str
    message: str

# -----------------------------
# Scam detection (lightweight)
# -----------------------------
SCAM_KEYWORDS = [
    "account", "blocked", "urgent", "verify",
    "click", "link", "upi", "bank", "payment"
]

def detect_scam(text: str) -> bool:
    return any(word in text.lower() for word in SCAM_KEYWORDS)

# -----------------------------
# Intelligence extraction
# -----------------------------
def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "urls": re.findall(r"https?://[^\s]+", text),
        "phone_numbers": re.findall(r"\b[6-9]\d{9}\b", text)
    }

def merge_intelligence(old, new):
    return {
        "upi_ids": list(set(old["upi_ids"] + new["upi_ids"])),
        "bank_accounts": list(set(old["bank_accounts"] + new["bank_accounts"])),
        "urls": list(set(old["urls"] + new["urls"])),
        "phone_numbers": list(set(old["phone_numbers"] + new["phone_numbers"])),
        "scam_type": "bank_impersonation"
    }

# -----------------------------
# LLM Agent
# -----------------------------
def llm_agent_reply(history: list):
    system_prompt = (
        "You are a normal, non-technical user. "
        "You must never accuse or mention scams. "
        "Be confused but cooperative. "
        "Ask clarifying questions to keep the conversation going."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-5:]:
        messages.append({"role": "user", "content": msg})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback (important for stability)
        return "I am a bit confused, can you please explain again?"

@app.get("/")
def health():
    return {"status": "API running"}

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/scam-agent")
def scam_agent(payload: ScamRequest):
    start_time = time.time()

    cid = payload.conversation_id
    msg = payload.message

    conversations.setdefault(cid, [])
    intelligence_store.setdefault(cid, {
        "upi_ids": [],
        "bank_accounts": [],
        "urls": [],
        "phone_numbers": [],
        "scam_type": "bank_impersonation"
    })

    conversations[cid].append(msg)
    turns = len(conversations[cid])

    scam_detected = detect_scam(msg)

    extracted_now = extract_intelligence(msg)
    intelligence_store[cid] = merge_intelligence(
        intelligence_store[cid],
        extracted_now
    )

    reply = (
        llm_agent_reply(conversations[cid])
        if scam_detected
        else "Hello"
    )

    return {
        "scam_detected": scam_detected,
        "agent_reply": reply,
        "engagement_metrics": {
            "turns": turns,
            "duration_seconds": int(time.time() - start_time)
        },
        "extracted_intelligence": intelligence_store[cid]
    }
