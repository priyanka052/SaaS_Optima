from fastapi import APIRouter

from app.db import SessionLocal
from app.models.pricing import Pricing


router = APIRouter(
    prefix="/api/pricing",
    tags=["pricing"]
)


@router.get("")
def get_pricing():
    with SessionLocal() as session:
        pricing = session.query(Pricing).all()

        return [
            {
                "id": item.id,
                "tool_id": item.tool_id,
                "plan": item.plan,
                "price": item.price,
                "currency": item.currency,
                "billing_period": item.billing_period,
                "source": item.source,
                "source_url": item.source_url,
                "last_updated": item.last_updated
            }
            for item in pricing
        ]