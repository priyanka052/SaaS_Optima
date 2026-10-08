from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing

from app.ml.deal_scoring import calculate_required_feature_coverage

from app.negotiation.graph import negotiation_graph
from app.negotiation.policy import (
    DEFAULT_VENDOR_POLICY,
    calculate_vendor_min_price,
)


router = APIRouter(
    prefix="/api/negotiation",
    tags=["negotiation"]
)


class NegotiationRequest(BaseModel):
    tool_name: str

    buyer_budget: float = Field(gt=0)

    required_features: list[str] = Field(
        default_factory=list
    )

    max_discount_percent: float = Field(
        default=DEFAULT_VENDOR_POLICY["max_discount_percent"],
        ge=0.0,
        le=50.0
    )

    contract_score: float = Field(
        default=DEFAULT_VENDOR_POLICY["contract_score"],
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
            base_price = pricing.price
            selected_plan = pricing.plan
            currency = pricing.currency

        elif tool.price_inr is not None:
            base_price = tool.price_inr
            selected_plan = None
            currency = "INR"

        else:
            raise HTTPException(
                status_code=404,
                detail=f"No pricing found for '{tool.name}'."
            )

        # Calculate feature coverage automatically.
        tool_features = [
            feature.strip()
            for feature in tool.features.split(";")
            if feature.strip()
        ]

        feature_coverage = calculate_required_feature_coverage(
            request.required_features,
            tool_features
        )

    vendor_min_price = calculate_vendor_min_price(
        base_price,
        request.max_discount_percent
    )

    initial_state = {
        "tool_name": tool.name,

        "base_price": base_price,
        "buyer_budget": request.buyer_budget,
        "vendor_min_price": vendor_min_price,

        "current_offer": None,
        "previous_offer": None,

        "round_number": 0,
        "max_rounds": request.max_rounds,

        "turn": "buyer",

        "history": [],
        "status": "negotiating",

        "final_price": None,

        "feature_coverage": feature_coverage,
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

        "required_features": request.required_features,
        "feature_coverage": result.get("feature_coverage"),

        "max_discount_percent": request.max_discount_percent,
        "vendor_min_price": vendor_min_price,

        "status": result.get("status"),
        "final_price": result.get("final_price"),

        "savings_percent": result.get("savings_percent"),
        "contract_score": result.get("contract_score"),
        "deal_score": result.get("deal_score"),

        "history": result.get("history", []),
    }