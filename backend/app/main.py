import os
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

app = FastAPI(title="!LERT Forensic Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    content: str
    mode: str = "Mode A: Quick Spot-Check"


class CheckoutSessionRequest(BaseModel):
    plan: str
    currency: str = "usd"
    success_url: str = "https://example.com/success"
    cancel_url: str = "https://example.com/cancel"


@app.get("/health/live")
def health_live():
    return {"status": "live", "service": "alert-intel"}


@app.get("/health/ready")
def health_ready():
    return {"status": "ready", "stripe_configured": bool(stripe.api_key)}


@app.post("/api/v1/scan")
def scan_artifact(payload: ScanRequest):
    text_lower = payload.content.lower()
    if "naomi" in text_lower and ("whatsapp" in text_lower or "transfer" in text_lower):
        verdict = "HIGH_CONFIDENCE_FRAUD"
        reasons = ["Identity/persona contradiction", "Behavioral grooming/pivot pattern"]
    elif any(k in text_lower for k in ["72", "receipt", "recruiter", "domain"]):
        verdict = "INCONSISTENCY_FLAGGED"
        reasons = ["Objective anomaly detected; awaiting second independent proof for Tier 4"]
    else:
        verdict = "UNVERIFIED_SPARSE"
        reasons = ["Insufficient public/registry data; zero hard contradictions"]

    return {
        "mode": payload.mode,
        "verdict": verdict,
        "reasons": reasons,
        "ephemeral_telemetry_purged": True,
    }


@app.post("/api/v1/billing/create-checkout-session")
def create_checkout_session(req: CheckoutSessionRequest):
    if not stripe.api_key:
        return {
            "mode": "simulated",
            "plan": req.plan,
            "currency": req.currency,
            "checkout_url": req.success_url,
        }

    unit_amount = 2900 if req.plan == "Guardian Pro" else 24900
    if req.currency.lower() == "ngn":
        unit_amount = 4500000 if req.plan == "Guardian Pro" else 38500000

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[
            {
                "price_data": {
                    "currency": req.currency.lower(),
                    "product_data": {"name": f"!LERT {req.plan}"},
                    "unit_amount": unit_amount,
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }
        ],
        success_url=req.success_url,
        cancel_url=req.cancel_url,
    )
    return {"id": session.id, "url": session.url}


@app.post("/api/v1/billing/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(default="")):
    raw_body = await request.body()
    if not STRIPE_WEBHOOK_SECRET:
        return {"received": True, "verified": False}
    try:
        event = stripe.Webhook.construct_event(raw_body, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"received": True, "event_type": event["type"]}
