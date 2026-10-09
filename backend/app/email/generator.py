def format_amount(value, currency="INR"):
    """Format a price using its currency."""
    if value is None:
        return "Not finalized"

    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency.upper(), f"{currency.upper()} ")
    return f"{symbol}{float(value):,.2f}"


def generate_negotiation_email(negotiation, currency="INR"):
    """Generate a professional email based on negotiation outcome."""

    tool_name = negotiation.tool_name
    status = (negotiation.status or "unknown").lower()

    base_price = format_amount(negotiation.base_price, currency)
    final_price = format_amount(negotiation.final_price, currency)

    savings = negotiation.savings_percent
    deal_score = negotiation.deal_score
    feature_coverage = negotiation.feature_coverage
    contract_score = negotiation.contract_score

    if status == "accepted":
        subject = f"Negotiation Successful — {tool_name}"

        body = f"""Hello,

We are pleased to confirm that the negotiation for {tool_name}
has been accepted through SaaSOptima.

NEGOTIATION SUMMARY
-------------------
SaaS Tool: {tool_name}
Original Price: {base_price}
Final Agreed Price: {final_price}
Savings: {f"{float(savings):.2f}%" if savings is not None else "N/A"}
Feature Coverage: {f"{float(feature_coverage):.2f}%" if feature_coverage is not None else "N/A"}
Contract Score: {contract_score if contract_score is not None else "N/A"}
Deal Score: {deal_score if deal_score is not None else "N/A"}

Please review the applicable subscription plan and contract terms
before finalizing the purchase.

This email summarizes the negotiation recorded in SaaSOptima.
It is not itself a binding contract or proof of purchase.

Best regards,
SaaSOptima Negotiation Assistant"""

    else:
        subject = f"Negotiation Outcome — {tool_name}"

        body = f"""Hello,

The negotiation for {tool_name} did not conclude with an
accepted agreement.

NEGOTIATION SUMMARY
-------------------
SaaS Tool: {tool_name}
Original Price: {base_price}
Negotiation Status: {status.replace("_", " ").title()}
Final Price: {final_price}
Deal Score: {deal_score if deal_score is not None else "N/A"}

You may review the negotiation history and reconsider the budget,
pricing requirements, or contract preferences before trying again.

This email summarizes the negotiation recorded in SaaSOptima.

Best regards,
SaaSOptima Negotiation Assistant"""

    return {
        "subject": subject,
        "body": body,
    }