from typing import TypedDict


class NegotiationState(TypedDict, total=False):
    tool_name: str

    base_price: float
    buyer_budget: float
    vendor_min_price: float

    current_offer: float | None
    previous_offer: float | None

    round_number: int
    max_rounds: int

    turn: str

    buyer_action: str
    vendor_action: str

    history: list

    status: str

    final_price: float | None

    # Deal scoring inputs/results
    feature_coverage: float
    contract_score: float
    savings_percent: float
    deal_score: float