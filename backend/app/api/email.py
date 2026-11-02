from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.negotiation import Negotiation
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.email.generator import generate_negotiation_email

router = APIRouter(
    prefix="/api/email",
    tags=["Email Generator"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{negotiation_id}")
def generate_email(
    negotiation_id: int,
    db: Session = Depends(get_db)
):
    """Generate an email for a saved negotiation."""

    negotiation = (
        db.query(Negotiation)
        .filter(Negotiation.id == negotiation_id)
        .first()
    )

    if negotiation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Negotiation {negotiation_id} not found"
        )

    # Resolve the currency from the tool's pricing records.
    currency = "INR"

    tool = (
        db.query(Tool)
        .filter(Tool.name.ilike(negotiation.tool_name))
        .first()
    )

    if tool is not None:
        pricing = (
            db.query(Pricing)
            .filter(Pricing.tool_id == tool.id)
            .filter(Pricing.billing_period.ilike("monthly"))
            .order_by(Pricing.price.asc())
            .first()
        )

        if pricing is not None and pricing.currency:
            currency = pricing.currency

    email = generate_negotiation_email(
        negotiation,
        currency=currency
    )

    return {
        "negotiation_id": negotiation.id,
        "tool_name": negotiation.tool_name,
        "status": negotiation.status,
        "currency": currency,
        "subject": email["subject"],
        "body": email["body"],
    }