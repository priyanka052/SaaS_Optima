from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.negotiation.graph import negotiation_graph


router = APIRouter(
    prefix="/api/negotiation",
    tags=["negotiation"]
)


class NegotiationRequest(BaseModel):
    tool_name: str
    buyer_budget: float = Field(gt=0)

    # Temporary until vendor discount/flexibility data
    # is added to the knowledge base.
    vendor_min_price: float = Field(gt=0)

    feature_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0
    )

    contract_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0
    )

    max_rounds: int = Field(
        default=6,
        ge=1,
        le=20
    )


@router.post("")
def start_negotiation(request: NegotiationRequest):

    with SessionLocal() as session:

        # Find the requested SaaS tool.
        tool = (
            session.query(Tool)
            .filter(Tool.name.ilike(request.tool_name))
            .first()
        )

        if not tool:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{request.tool_name}' not found."
            )

        # Find the cheapest available monthly plan.
        pricing = (
            session.query(Pricing)
            .filter(
                Pricing.tool_id == tool.id,
                Pricing.billing_period == "monthly"
            )
            .order_by(Pricing.price.asc())
            .first()
        )

        # Prefer the Pricing table.
        if pricing:
            base_price = pricing.price
            selected_plan = pricing.plan
            currency = pricing.currency
        elif tool.price_inr is not None:
            # Backward-compatible fallback.
            base_price = tool.price_inr
            selected_plan = None
            currency = "INR"
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No pricing found for '{tool.name}'."
            )

    initial_state = {
        "tool_name": tool.name,

        "base_price": base_price,
        "buyer_budget": request.buyer_budget,
        "vendor_min_price": request.vendor_min_price,

        "current_offer": None,
        "previous_offer": None,

        "round_number": 0,
        "max_rounds": request.max_rounds,

        "turn": "buyer",

        "history": [],
        "status": "negotiating",

        "final_price": None,

        "feature_coverage": request.feature_coverage,
        "contract_score": request.contract_score,

        "savings_percent": 0.0,
        "deal_score": 0.0,
    }

    result = negotiation_graph.invoke(initial_state)

    return {
        "tool_name": result.get("tool_name"),
        "plan": selected_plan,
        "currency": currency,
        "base_price": base_price,
        "buyer_budget": request.buyer_budget,
        "vendor_min_price": request.vendor_min_price,
        "status": result.get("status"),
        "final_price": result.get("final_price"),
        "savings_percent": result.get("savings_percent"),
        "feature_coverage": result.get("feature_coverage"),
        "contract_score": result.get("contract_score"),
        "deal_score": result.get("deal_score"),
        "history": result.get("history", []),
    }