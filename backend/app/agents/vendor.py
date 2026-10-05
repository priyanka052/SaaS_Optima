def vendor_agent(state):
    current_offer = state["current_offer"]
    vendor_min_price = state["vendor_min_price"]
    max_rounds = state["max_rounds"]
    round_number = state["round_number"]

    history = state.get("history", [])

    # Vendor accepts an offer that meets its minimum.
    if current_offer >= vendor_min_price:
        history.append({
            "agent": "vendor",
            "action": "accept",
            "offer": current_offer
        })

        return {
            "vendor_action": "accept",
            "status": "accepted",
            "final_price": current_offer,
            "history": history
        }

    if round_number >= max_rounds:
        history.append({
            "agent": "vendor",
            "action": "reject",
            "offer": current_offer
        })

        return {
            "vendor_action": "reject",
            "status": "rejected",
            "history": history
        }

    # Vendor makes a concession toward its minimum.
    counter_offer = round(
        current_offer + (vendor_min_price - current_offer) * 0.5,
        2
    )

    # Never go below vendor minimum.
    counter_offer = max(counter_offer, vendor_min_price)

    history.append({
        "agent": "vendor",
        "action": "counter_offer",
        "offer": counter_offer
    })

    return {
        "previous_offer": current_offer,
        "current_offer": counter_offer,
        "vendor_action": "counter_offer",
        "turn": "buyer",
        "history": history,
        "status": "negotiating"
    }