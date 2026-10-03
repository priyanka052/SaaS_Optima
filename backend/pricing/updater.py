import requests
import re
from bs4 import BeautifulSoup

from app.db import SessionLocal
from app.models.pricing import Pricing
from app.models.tool import Tool

def scrape_slack_pricing():
    url = "https://slack.com/pricing"

    with SessionLocal() as session:
        tool = session.query(Tool).filter(Tool.name == "Slack").first()

    if not tool:
        print("Slack tool not found in database.")
        return []
    print("Slack tool ID:", tool.id)
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    plan_containers = soup.find_all(
        "div",
        class_=re.compile(r"plan-type-")
    )

    for container in plan_containers:
        classes = container.get("class", [])

        plan_class = next(
            (c for c in classes if c.startswith("plan-type-")),
            None
        )

        if not plan_class:
            continue

        plan_name = plan_class.replace("plan-type--", "").title()

        plan_text = container.get_text(" ", strip=True)

        yearly = re.findall(
            r"₹([\d,]+(?:\.\d+)?)\s+per user/month,\s+when paying yearly",
            plan_text
        )

        monthly = re.findall(
            r"₹([\d,]+(?:\.\d+)?)\s+per user/month,\s+when paying monthly",
            plan_text
        )

        pricing_data.append({
            "plan": plan_name,
            "yearly_price": float(yearly[0]) if yearly else None,
            "monthly_price": float(monthly[0]) if monthly else None,
            "currency": "INR",
            "source": "slack",
            "source_url": url,
        })

    with SessionLocal() as session:
        for item in pricing_data:
            if item["yearly_price"] is not None:
                session.add(
                    Pricing(
                        tool_id=tool.id,
                        plan=item["plan"],
                        price=item["yearly_price"],
                        currency=item["currency"],
                        billing_period="yearly",
                        source=item["source"],
                        source_url=item["source_url"],
                    )
                )

            if item["monthly_price"] is not None:
                session.add(
                    Pricing(
                        tool_id=tool.id,
                        plan=item["plan"],
                        price=item["monthly_price"],
                        currency=item["currency"],
                        billing_period="monthly",
                        source=item["source"],
                        source_url=item["source_url"],
                    )
                )

        session.commit()
    
    return pricing_data



if __name__ == "__main__":
    data = scrape_slack_pricing()

    for item in data:
        print(item)