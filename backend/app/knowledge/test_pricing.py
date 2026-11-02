from app.knowledge.pricing import (
    get_tool_pricing,
    get_cheapest_monthly_price,
)


pricing = get_tool_pricing("Slack")

print("All Slack pricing:")
print(pricing)


cheapest = get_cheapest_monthly_price("Slack")

print("\nCheapest monthly Slack price:")
print(cheapest)