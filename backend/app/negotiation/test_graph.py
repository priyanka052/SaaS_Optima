from app.negotiation.graph import negotiation_graph


initial_state = {
    "tool_name": "Slack",

    "base_price": 294.75,
    "buyer_budget": 270.0,
    "vendor_min_price": 260.0,

    "current_offer": None,
    "previous_offer": None,

    "round_number": 0,
    "max_rounds": 6,

    "turn": "buyer",

    "history": [],
    "status": "negotiating",

    "final_price": None,

    # These will later come automatically
    # from overlap/knowledge-base data.
    "feature_coverage": 66.67,
    "contract_score": 80.0,

    "savings_percent": 0.0,
    "deal_score": 0.0,
}


result = negotiation_graph.invoke(initial_state)


print("Status:", result.get("status"))
print("Final price:", result.get("final_price"))
print("Savings %:", result.get("savings_percent"))
print("Feature coverage:", result.get("feature_coverage"))
print("Contract score:", result.get("contract_score"))
print("Deal score:", result.get("deal_score"))

print("\nNegotiation history:")

for item in result.get("history", []):
    print(
        f"{item['agent'].upper()} | "
        f"{item['action']} | "
        f"₹{item['offer']}"
    )