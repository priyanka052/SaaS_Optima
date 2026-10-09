from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import SessionLocal
from app.models.tool import Tool
from app.models.pricing import Pricing
from app.models.negotiation import Negotiation
from app.models.negotiation_turn import NegotiationTurn

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

    # Step 1: Find the tool and its cheapest monthly plan.
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

        tool_name = tool.name

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
                detail=f"No pricing found for '{tool_name}'."
            )

        # Calculate feature coverage from the tool's actual features.
        tool_features = [
            feature.strip()
            for feature in tool.features.split(";")
            if feature.strip()
        ]

        feature_coverage = calculate_required_feature_coverage(
            request.required_features,
            tool_features
        )

    # Step 2: Apply the configurable vendor negotiation policy.
    vendor_min_price = calculate_vendor_min_price(
        base_price,
        request.max_discount_percent
    )

    # Step 3: Prepare the LangGraph initial state.
    initial_state = {
        "tool_name": tool_name,
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

    # Step 4: Run Buyer Agent <-> Vendor Agent negotiation.
    result = negotiation_graph.invoke(initial_state)

    # Step 5: Persist the negotiation and its audit history.
    with SessionLocal() as session:

        negotiation = Negotiation(
            tool_name=tool_name,
            base_price=base_price,
            buyer_budget=request.buyer_budget,
            final_price=result.get("final_price"),
            status=result.get("status", "unknown"),
            savings_percent=result.get("savings_percent", 0.0),
            feature_coverage=result.get("feature_coverage", 0.0),
            contract_score=result.get("contract_score", 0.0),
            deal_score=result.get("deal_score", 0.0),
            completed_at=datetime.utcnow(),
        )

        session.add(negotiation)

        # Obtain the database ID before saving the turns.
        session.flush()

        negotiation_id = negotiation.id

        for turn_number, event in enumerate(
            result.get("history", []),
            start=1
        ):
            session.add(
                NegotiationTurn(
                    negotiation_id=negotiation_id,
                    round_number=turn_number,
                    agent=event.get("agent", "unknown"),
                    action=event.get("action", "unknown"),
                    offer=event.get("offer"),
                )
            )

        # Save the negotiation and all its turns together.
        session.commit()

    # Step 6: Return the result, including its persistent ID.
    return {
        "negotiation_id": negotiation_id,
        "tool_name": tool_name,
        "plan": selected_plan,
        "currency": currency,

        "base_price": base_price,
        "buyer_budget": request.buyer_budget,
        "vendor_min_price": vendor_min_price,
        "max_discount_percent": request.max_discount_percent,

        "required_features": request.required_features,
        "feature_coverage": result.get("feature_coverage"),
        "contract_score": result.get("contract_score"),

        "status": result.get("status"),
        "final_price": result.get("final_price"),
        "savings_percent": result.get("savings_percent"),
        "deal_score": result.get("deal_score"),

        "history": result.get("history", []),
    }