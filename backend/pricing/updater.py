import requests;
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from app.db import SessionLocal
from app.models.pricing import Pricing
from app.models.tool import Tool


def save_pricing(tool_name, pricing_data):

    with SessionLocal() as session:

        tool = session.query(Tool).filter(
            Tool.name == tool_name
        ).first()

        if not tool:
            print(f"{tool_name} tool not found in database.")
            return

        for item in pricing_data:

            if item["price"] is None:
                continue

            existing = session.query(Pricing).filter(
                Pricing.tool_id == tool.id,
                Pricing.plan == item["plan"],
                Pricing.billing_period == item["billing_period"],
                Pricing.source == item["source"],
            ).first()

            if existing:
                existing.price = item["price"]
                existing.currency = item["currency"]
                existing.source_url = item["source_url"]

            else:
                session.add(
                    Pricing(
                        tool_id=tool.id,
                        plan=item["plan"],
                        price=item["price"],
                        currency=item["currency"],
                        billing_period=item["billing_period"],
                        source=item["source"],
                        source_url=item["source_url"],
                    )
                )

        session.commit()

# ============================================================
# SLACK PRICING
# ============================================================

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
            "price": float(yearly[0]) if yearly else None,
            "currency": "INR",
            "billing_period": "yearly",
            "source": "slack",
            "source_url": url,
        })

    # Save Slack pricing to database
    save_pricing("Slack", pricing_data)

    return pricing_data

    return pricing_data

# ============================================================
# MICROSOFT TEAMS PRICING
# ============================================================

def scrape_teams_pricing():

    url = (
        "https://www.microsoft.com/en-in/"
        "microsoft-teams/compare-microsoft-teams-business-options"
    )

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []
    seen = set()

    for container in soup.select(".sku"):

        title = container.select_one(".oc-product-title")
        price = container.select_one(".oc-displayListPrice")
        billing = container.select_one(".oc-displayUnit")

        if not title or not price or not billing:
            continue

        plan = title.get_text(" ", strip=True)

        if plan not in [
            "Microsoft Teams Essentials",
            "Microsoft Teams Premium"
        ]:
            continue

        price_text = price.get_text(" ", strip=True)
        billing_text = billing.get_text(" ", strip=True)

        key = (plan, price_text, billing_text)

        if key in seen:
            continue

        seen.add(key)

        price_value = re.sub(r"[^\d.]", "", price_text)

        pricing_data.append({
            "plan": plan,
            "price": float(price_value),
            "currency": "INR",
            "billing_period": "yearly",
            "source": "microsoft_teams",
            "source_url": url,
        })

    # Save Teams pricing to database
    save_pricing("Microsoft Teams", pricing_data)

    return pricing_data


# ============================================================
# ZOOM PRICING
# ============================================================

def scrape_zoom_pricing():

    url = "https://zoom.us/billing/pricing"

    params = {
        "pageType": "workplace",
        "callFrom": "IN"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    pricing_data = []

    for product in data["result"].get("productList", []):

        plan_name = product.get("categoryCode")

        # Keep only the main Zoom Workplace plans
        if plan_name not in ["PRO", "ZOPRO", "BIZ"]:
            continue

        for item in product.get("items", []):

            if item.get("price") is None:
                continue

            pricing_data.append({
                "plan": plan_name,
                "price": item["price"] / 100,
                "currency": item.get("currency", "USD"),
                "billing_period": (
                    "monthly"
                    if item.get("billingCycle") == 1
                    else "yearly"
                ),
                "source": "zoom",
                "source_url": url,
            })

    # Save Zoom pricing to database
    save_pricing("Zoom", pricing_data)

    return pricing_data


# ============================================================
# TEST ALL SCRAPERS
# ============================================================

if __name__ == "__main__":

    print("Slack pricing:")

    for item in scrape_slack_pricing():
        print(item)

    print("\nMicrosoft Teams pricing:")

    for item in scrape_teams_pricing():
        print(item)

    print("\nZoom pricing:")

    for item in scrape_zoom_pricing():
        print(item)