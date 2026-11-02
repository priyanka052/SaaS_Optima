from app.negotiation.policy import calculate_vendor_counter_offer


def vendor_agent(state):
    current_offer = state["current_offer"]
    vendor_min_price = state["vendor_min_price"]
    base_price = state["base_price"]

    max_rounds = state["max_rounds"]
    round_number = state["round_number"]

    history = list(state.get("history", []))

    # Vendor accepts offers that meet its minimum.
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
            "offer": current_offer,
            "reason": "Maximum negotiation rounds reached."
        })

        return {
            "vendor_action": "reject",
            "status": "rejected",
            "history": history
        }

    # Vendor makes a strategic counteroffer.
    counter_offer = calculate_vendor_counter_offer(
        base_price,
        vendor_min_price,
        round_number
    )

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