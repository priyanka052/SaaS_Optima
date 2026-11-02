from app.negotiation.policy import calculate_buyer_opening_offer


def buyer_agent(state):
    base_price = state["base_price"]
    buyer_budget = state["buyer_budget"]
    vendor_min_price = state["vendor_min_price"]

    current_offer = state.get("current_offer")
    round_number = state.get("round_number", 0)
    max_rounds = state["max_rounds"]

    history = list(state.get("history", []))

    # Check whether an agreement is financially possible.
    if buyer_budget < vendor_min_price:
        history.append({
            "agent": "buyer",
            "action": "reject",
            "reason": "Buyer budget is below vendor minimum price."
        })

        return {
            "buyer_action": "reject",
            "status": "rejected",
            "history": history
        }

    # Buyer makes the opening offer.
    if current_offer is None:
        opening_offer = calculate_buyer_opening_offer(
            base_price,
            buyer_budget
        )

        history.append({
            "agent": "buyer",
            "action": "opening_offer",
            "offer": opening_offer
        })

        return {
            "current_offer": opening_offer,
            "buyer_action": "opening_offer",
            "turn": "vendor",
            "round_number": 1,
            "history": history,
            "status": "negotiating"
        }

    # Buyer receives a vendor counteroffer.
    if current_offer <= buyer_budget:
        history.append({
            "agent": "buyer",
            "action": "accept",
            "offer": current_offer
        })

        return {
            "buyer_action": "accept",
            "status": "accepted",
            "final_price": current_offer,
            "history": history
        }

    if round_number >= max_rounds:
        history.append({
            "agent": "buyer",
            "action": "reject",
            "offer": current_offer,
            "reason": "Maximum negotiation rounds reached."
        })

        return {
            "buyer_action": "reject",
            "status": "rejected",
            "history": history
        }

    # Buyer counters at their maximum affordable budget.
    new_offer = round(buyer_budget, 2)

    history.append({
        "agent": "buyer",
        "action": "counter_offer",
        "offer": new_offer
    })

    return {
        "previous_offer": current_offer,
        "current_offer": new_offer,
        "buyer_action": "counter_offer",
        "turn": "vendor",
        "round_number": round_number + 1,
        "history": history,
        "status": "negotiating"
    }