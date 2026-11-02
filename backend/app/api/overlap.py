
from fastapi import APIRouter, Query

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.ml.overlap import compare_features


router = APIRouter(
    prefix="/api/overlap",
    tags=["overlap"]
)


def build_pricing_lookup(pricing_rows):
    """Get the cheapest monthly price per tool and currency."""
    lookup = {}

    for item in pricing_rows:
        if item.price < 0:
            continue

        currency = (item.currency or "INR").upper()
        key = (item.tool_id, currency)

        if key not in lookup or item.price < lookup[key]["price"]:
            lookup[key] = {
                "price": item.price,
                "currency": currency,
                "plan": item.plan,
                "billing_period": item.billing_period
            }

    return lookup


def get_tool_price(tool, lookup):
    """Prefer monthly pricing records, then use legacy INR price."""
    matching = {
        currency: details
        for (tool_id, currency), details in lookup.items()
        if tool_id == tool.id
    }

    if "INR" in matching:
        return matching["INR"]

    if tool.price_inr is not None:
        return {
            "price": tool.price_inr,
            "currency": "INR",
            "plan": None,
            "billing_period": "monthly"
        }

    if matching:
        currency = sorted(matching.keys())[0]
        return matching[currency]

    return {
        "price": None,
        "currency": None,
        "plan": None,
        "billing_period": None
    }


@router.get("")
def get_overlap(
    threshold: float = Query(
        default=0.0,
        ge=0.0,
        le=100.0
    )
):
    with SessionLocal() as session:
        tools = session.query(Tool).order_by(Tool.name).all()

        pricing_rows = (
            session.query(Pricing)
            .filter(Pricing.billing_period == "monthly")
            .all()
        )

        pricing_lookup = build_pricing_lookup(pricing_rows)

        results = []

        for i in range(len(tools)):
            for j in range(i + 1, len(tools)):
                tool_a = tools[i]
                tool_b = tools[j]

                comparison = compare_features(
                    tool_a.features,
                    tool_b.features
                )

                similarity = comparison["similarity"]

                if similarity < threshold:
                    continue

                pricing_a = get_tool_price(tool_a, pricing_lookup)
                pricing_b = get_tool_price(tool_b, pricing_lookup)

                price_a = pricing_a["price"]
                price_b = pricing_b["price"]

                same_currency = (
                    pricing_a["currency"] is not None
                    and pricing_a["currency"] == pricing_b["currency"]
                )

                recommended_tool = None
                potential_savings = None

                if (
                    price_a is not None
                    and price_b is not None
                    and same_currency
                ):
                    if price_a <= price_b:
                        recommended_tool = tool_a.name
                        potential_savings = round(price_b - price_a, 2)
                    else:
                        recommended_tool = tool_b.name
                        potential_savings = round(price_a - price_b, 2)

                results.append({
                    "tool_a": tool_a.name,
                    "tool_b": tool_b.name,
                    "similarity": similarity,
                    "common_features": comparison["common_features"],
                    "unique_features_a": comparison["unique_features_a"],
                    "unique_features_b": comparison["unique_features_b"],
                    "price_a": price_a,
                    "currency_a": pricing_a["currency"],
                    "plan_a": pricing_a["plan"],
                    "price_b": price_b,
                    "currency_b": pricing_b["currency"],
                    "plan_b": pricing_b["plan"],
                    "recommended_tool": recommended_tool,
                    "potential_monthly_savings": potential_savings,
                    "pricing_comparable": same_currency
                })

        results.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return results
