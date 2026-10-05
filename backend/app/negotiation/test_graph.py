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
    "savings_percent": None,
}


result = negotiation_graph.invoke(initial_state)

print("Status:", result.get("status"))
print("Final price:", result.get("final_price"))

print("\nNegotiation history:")

for item in result.get("history", []):
    print(
        f"{item['agent'].upper()} | "
        f"{item['action']} | "
        f"₹{item['offer']}"
    )