
from fastapi import APIRouter, HTTPException, Query

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.ml.overlap import compare_features


router = APIRouter(
    prefix="/api/compare",
    tags=["compare"]
)


def get_monthly_price(session, tool, currency="INR", plan=None):
    """Get the cheapest monthly price in the requested currency."""

    query = session.query(Pricing).filter(
        Pricing.tool_id == tool.id,
        Pricing.billing_period.ilike("monthly"),
        Pricing.currency.ilike(currency)
    )

    if plan:
        query = query.filter(Pricing.plan.ilike(plan))

    pricing = query.order_by(Pricing.price.asc()).first()

    if pricing:
        return {
            "price": pricing.price,
            "plan": pricing.plan,
            "currency": pricing.currency,
            "source": pricing.source,
            "source_url": pricing.source_url,
            "last_updated": pricing.last_updated.isoformat()
            if pricing.last_updated else None,
        }

    if currency.upper() == "INR" and not plan and tool.price_inr is not None:
        return {
            "price": tool.price_inr,
            "plan": None,
            "currency": "INR",
            "source": "tools",
            "source_url": tool.url,
            "last_updated": None,
        }

    return {
        "price": None,
        "plan": None,
        "currency": currency.upper(),
        "source": None,
        "source_url": None,
        "last_updated": None,
    }


@router.get("")
def compare_tools(
    tool_a: str = Query(..., min_length=1),
    tool_b: str = Query(..., min_length=1),
    currency: str = Query(default="INR", min_length=3, max_length=3),
    plan: str = Query(default=None, min_length=1),
):
    currency = currency.strip().upper()

    if not currency.isalpha():
        raise HTTPException(
            status_code=400,
            detail="Currency must be a three-letter code."
        )

    with SessionLocal() as session:
        tool_a_obj = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_a.strip()))
            .first()
        )

        tool_b_obj = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_b.strip()))
            .first()
        )

        if not tool_a_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_a}' not found."
            )

        if not tool_b_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_b}' not found."
            )

        feature_comparison = compare_features(
            tool_a_obj.features,
            tool_b_obj.features
        )

        pricing_a = get_monthly_price(
            session, tool_a_obj, currency, plan
        )

        pricing_b = get_monthly_price(
            session, tool_b_obj, currency, plan
        )

        price_a = pricing_a["price"]
        price_b = pricing_b["price"]

        comparable = price_a is not None and price_b is not None

        cheaper_tool = None
        monthly_savings = None

        if comparable:
            if price_a <= price_b:
                cheaper_tool = tool_a_obj.name
                monthly_savings = round(price_b - price_a, 2)
            else:
                cheaper_tool = tool_b_obj.name
                monthly_savings = round(price_a - price_b, 2)

        return {
            "tool_a": {
                "name": tool_a_obj.name,
                "category": tool_a_obj.category,
                **pricing_a,
            },
            "tool_b": {
                "name": tool_b_obj.name,
                "category": tool_b_obj.category,
                **pricing_b,
            },
            "overlap": feature_comparison,
            "recommendation": {
                "cheaper_tool": cheaper_tool,
                "potential_monthly_savings": monthly_savings,
                "currency": currency,
                "pricing_comparable": comparable,
                "message": (
                    "Prices compared using monthly billing "
                    "in the same currency."
                    if comparable
                    else "Comparable pricing is unavailable."
                ),
            },
        }
