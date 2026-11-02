
from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing


def get_tool_pricing(tool_name):
    """Return all pricing records for a SaaS tool."""

    with SessionLocal() as session:
        tool = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_name.strip()))
            .first()
        )

        if not tool:
            return None

        records = (
            session.query(Pricing)
            .filter(Pricing.tool_id == tool.id)
            .order_by(Pricing.plan.asc(), Pricing.price.asc())
            .all()
        )

        return {
            "tool_id": tool.id,
            "tool_name": tool.name,
            "pricing": [
                {
                    "plan": record.plan,
                    "price": record.price,
                    "currency": record.currency,
                    "billing_period": record.billing_period,
                    "source": record.source,
                    "source_url": record.source_url,
                    "last_updated": record.last_updated.isoformat()
                    if record.last_updated else None,
                }
                for record in records
            ],
        }


def get_cheapest_monthly_price(tool_name, currency="INR", plan=None):
    """Get the cheapest monthly price in the requested currency."""

    with SessionLocal() as session:
        tool = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_name.strip()))
            .first()
        )

        if not tool:
            return None

        query = session.query(Pricing).filter(
            Pricing.tool_id == tool.id,
            Pricing.billing_period.ilike("monthly"),
            Pricing.currency.ilike(currency.strip()),
        )

        if plan:
            query = query.filter(Pricing.plan.ilike(plan.strip()))

        pricing = query.order_by(Pricing.price.asc()).first()

        if pricing:
            return {
                "plan": pricing.plan,
                "price": pricing.price,
                "currency": pricing.currency,
                "billing_period": pricing.billing_period,
                "source": pricing.source,
                "source_url": pricing.source_url,
                "last_updated": pricing.last_updated.isoformat()
                if pricing.last_updated else None,
            }

        if (
            currency.strip().upper() == "INR"
            and not plan
            and tool.price_inr is not None
        ):
            return {
                "plan": None,
                "price": tool.price_inr,
                "currency": "INR",
                "billing_period": "monthly",
                "source": "tools",
                "source_url": tool.url,
                "last_updated": None,
            }

        return None


def compare_monthly_pricing(tool_a, tool_b, currency="INR", plan=None):
    """Compare two tools without mixing currencies or billing periods."""

    price_a = get_cheapest_monthly_price(tool_a, currency, plan)
    price_b = get_cheapest_monthly_price(tool_b, currency, plan)

    result = {
        "currency": currency.upper(),
        "tool_a_pricing": price_a,
        "tool_b_pricing": price_b,
        "comparable": False,
        "cheaper_tool": None,
        "monthly_savings": None,
    }

    if price_a is None or price_b is None:
        result["message"] = "Comparable monthly pricing is unavailable."
        return result

    result["comparable"] = True

    if price_a["price"] <= price_b["price"]:
        result["cheaper_tool"] = tool_a
        result["monthly_savings"] = round(
            price_b["price"] - price_a["price"], 2
        )
    else:
        result["cheaper_tool"] = tool_b
        result["monthly_savings"] = round(
            price_a["price"] - price_b["price"], 2
        )

    return result
