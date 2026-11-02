def buyer_agent(state):
    base_price = state["base_price"]
    buyer_budget = state["buyer_budget"]
    current_offer = state.get("current_offer")
    turn = state.get("turn", "buyer")
    round_number = state.get("round_number", 0)
    max_rounds = state["max_rounds"]

    history = state.get("history", [])

    # Buyer makes the opening offer.
    if current_offer is None:
        opening_offer = min(
            buyer_budget,
            round(base_price * 0.85, 2)
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

    # Buyer receives a vendor offer.
    if turn == "buyer":

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
                "offer": current_offer
            })

            return {
                "buyer_action": "reject",
                "status": "rejected",
                "history": history
            }

        # Buyer makes a concession.
        new_offer = round(current_offer * 0.95, 2)

        if new_offer > buyer_budget:
            new_offer = buyer_budget

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

    return {}