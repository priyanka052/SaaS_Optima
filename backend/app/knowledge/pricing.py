from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing


def get_tool_pricing(tool_name):
    """
    Return all pricing records for a SaaS tool.
    The database is the primary source of truth.
    """

    with SessionLocal() as session:
        tool = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_name))
            .first()
        )

        if not tool:
            return None

        pricing_records = (
            session.query(Pricing)
            .filter(Pricing.tool_id == tool.id)
            .order_by(
                Pricing.billing_period.asc(),
                Pricing.price.asc()
            )
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
                    "last_updated": record.last_updated,
                }
                for record in pricing_records
            ]
        }


def get_cheapest_monthly_price(tool_name):
    """
    Return the cheapest available monthly plan for a tool.
    """

    with SessionLocal() as session:
        tool = (
            session.query(Tool)
            .filter(Tool.name.ilike(tool_name))
            .first()
        )

        if not tool:
            return None

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
                "plan": pricing.plan,
                "price": pricing.price,
                "currency": pricing.currency,
                "source": pricing.source,
                "source_url": pricing.source_url,
            }

        if tool.price_inr is not None:
            return {
                "plan": None,
                "price": tool.price_inr,
                "currency": "INR",
                "source": "tools",
                "source_url": tool.url,
            }

        return None