from fastapi import APIRouter, HTTPException, Query

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.ml.overlap import jaccard_similarity, parse_features


router = APIRouter(
    prefix="/api/compare",
    tags=["compare"]
)


def get_monthly_price(session, tool):
    """
    Get the cheapest available monthly price for a tool.

    Pricing table is preferred. Tool.price_inr is used as
    a backward-compatible fallback.
    """

    pricing = (
        session.query(Pricing)
        .filter(
            Pricing.tool_id == tool.id,
            Pricing.billing_period == "monthly"
        )
        .order_by(Pricing.price.asc())
        .first()
    )

    if pricing:
        return {
            "price": pricing.price,
            "plan": pricing.plan,
            "currency": pricing.currency
        }

    if tool.price_inr is not None:
        return {
            "price": tool.price_inr,
            "plan": None,
            "currency": "INR"
        }

    return {
        "price": None,
        "plan": None,
        "currency": None
    }


@router.get("")
def compare_tools(
    tool_a: str = Query(..., min_length=1),
    tool_b: str = Query(..., min_length=1)
):
    with SessionLocal() as session:

        tool_a_obj = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_a))
            .first()
        )

        tool_b_obj = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_b))
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

        features_a = parse_features(tool_a_obj.features)
        features_b = parse_features(tool_b_obj.features)

        set_a = set(features_a)
        set_b = set(features_b)

        common_features = sorted(set_a.intersection(set_b))
        unique_features_a = sorted(set_a - set_b)
        unique_features_b = sorted(set_b - set_a)

        score = jaccard_similarity(
            features_a,
            features_b
        )

        similarity = round(score * 100, 2)

        pricing_a = get_monthly_price(
            session,
            tool_a_obj
        )

        pricing_b = get_monthly_price(
            session,
            tool_b_obj
        )

        price_a = pricing_a["price"]
        price_b = pricing_b["price"]

        cheaper_tool = None
        monthly_savings = None

        if price_a is not None and price_b is not None:
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
                "price": price_a,
                "plan": pricing_a["plan"],
                "currency": pricing_a["currency"]
            },
            "tool_b": {
                "name": tool_b_obj.name,
                "category": tool_b_obj.category,
                "price": price_b,
                "plan": pricing_b["plan"],
                "currency": pricing_b["currency"]
            },
            "overlap": {
                "similarity": similarity,
                "common_features": common_features,
                "unique_features_a": unique_features_a,
                "unique_features_b": unique_features_b
            },
            "recommendation": {
                "cheaper_tool": cheaper_tool,
                "potential_monthly_savings": monthly_savings
            }
        }