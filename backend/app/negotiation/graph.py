from langgraph.graph import StateGraph, START, END

from app.negotiation.state import NegotiationState
from app.agents.buyer import buyer_agent
from app.agents.vendor import vendor_agent

from app.ml.deal_scoring import (
    calculate_savings_percent,
    calculate_deal_score,
)


def buyer_node(state: NegotiationState):
    return buyer_agent(state)


def vendor_node(state: NegotiationState):
    return vendor_agent(state)


def deal_scoring_node(state: NegotiationState):
    """
    Calculate the final deal score after negotiation ends.
    """

    if state.get("status") != "accepted":
        return {
            "savings_percent": 0.0,
            "deal_score": 0.0,
        }

    base_price = state["base_price"]
    final_price = state["final_price"]

    savings_percent = calculate_savings_percent(
        base_price,
        final_price
    )

    feature_coverage = state.get("feature_coverage", 0.0)
    contract_score = state.get("contract_score", 0.0)

    deal_score = calculate_deal_score(
        savings_percent,
        feature_coverage,
        contract_score
    )

    return {
        "savings_percent": savings_percent,
        "deal_score": deal_score,
    }


def should_continue_after_buyer(state: NegotiationState):
    if state.get("status") in {"accepted", "rejected"}:
        return "score"

    return "vendor"


def should_continue_after_vendor(state: NegotiationState):
    if state.get("status") in {"accepted", "rejected"}:
        return "score"

    return "buyer"


graph_builder = StateGraph(NegotiationState)

graph_builder.add_node("buyer", buyer_node)
graph_builder.add_node("vendor", vendor_node)
graph_builder.add_node("score", deal_scoring_node)

graph_builder.add_edge(START, "buyer")

graph_builder.add_conditional_edges(
    "buyer",
    should_continue_after_buyer,
)

graph_builder.add_conditional_edges(
    "vendor",
    should_continue_after_vendor,
)

graph_builder.add_edge("score", END)

negotiation_graph = graph_builder.compile()