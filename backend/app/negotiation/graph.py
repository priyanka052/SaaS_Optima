from langgraph.graph import StateGraph, START, END

from app.negotiation.state import NegotiationState
from app.agents.buyer import buyer_agent
from app.agents.vendor import vendor_agent


def buyer_node(state: NegotiationState):
    return buyer_agent(state)


def vendor_node(state: NegotiationState):
    return vendor_agent(state)


def should_continue_after_buyer(state: NegotiationState):
    if state.get("status") in {"accepted", "rejected"}:
        return END

    return "vendor"


def should_continue_after_vendor(state: NegotiationState):
    if state.get("status") in {"accepted", "rejected"}:
        return END

    return "buyer"


graph_builder = StateGraph(NegotiationState)

graph_builder.add_node("buyer", buyer_node)
graph_builder.add_node("vendor", vendor_node)

graph_builder.add_edge(START, "buyer")

graph_builder.add_conditional_edges(
    "buyer",
    should_continue_after_buyer,
)

graph_builder.add_conditional_edges(
    "vendor",
    should_continue_after_vendor,
)

negotiation_graph = graph_builder.compile()