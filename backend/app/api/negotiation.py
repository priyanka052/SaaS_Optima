from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.negotiation.graph import negotiation_graph


router = APIRouter(
    prefix="/api/negotiation",
    tags=["negotiation"]
)


class NegotiationRequest(BaseModel):
    tool_name: str
    base_price: float = Field(gt=0)
    buyer_budget: float = Field(gt=0)
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
    initial_state = {
        "tool_name": request.tool_name,

        "base_price": request.base_price,
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
        "status": result.get("status"),
        "final_price": result.get("final_price"),
        "savings_percent": result.get("savings_percent"),
        "feature_coverage": result.get("feature_coverage"),
        "contract_score": result.get("contract_score"),
        "deal_score": result.get("deal_score"),
        "history": result.get("history", []),
    }