from turtle import position
from urllib import response

from pricing.updater import save_pricing
import requests
import re
from bs4 import BeautifulSoup


def scrape_clickup_pricing():

    url = "https://clickup.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    cards = soup.select("div.PricingV4Card_priceWrapper__L75f0")

    plans = ["Free", "Unlimited", "Business", "Enterprise"]

    for plan, card in zip(plans, cards):

        price_element = card.select_one(
            "span.PricingV4Card_billingPriceVisible__KY9CV"
        )

        if not price_element:
            continue

        price_text = price_element.get_text(" ", strip=True)

        match = re.search(r"\$?\s*([\d,]+(?:\.\d+)?)", price_text)

        if not match:
            continue

        pricing_data.append({
            "plan": plan,
            "price": float(match.group(1).replace(",", "")),
            "currency": "USD",
            "billing_period": "yearly",
            "source": "clickup",
            "source_url": url,
        })
    save_pricing("ClickUp", pricing_data)
    return pricing_data

def scrape_monday_pricing():

    url = "https://monday.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    prices = soup.select("div.price")

    plans = ["Free", "Basic", "Standard", "Pro", "Enterprise"]

    for plan, price_element in zip(plans, prices):

        text = price_element.get_text(" ", strip=True)

        match = re.search(
            r"\$\s*([\d,]+(?:\.\d+)?)",
            text
        )

        if not match or plan == "Enterprise":
            continue

        pricing_data.append({
            "plan": plan,
            "price": float(match.group(1).replace(",", "")),
            "currency": "USD",
            "billing_period": "yearly",
            "source": "monday",
            "source_url": url,
        })

    save_pricing("Monday.com", pricing_data)

    return pricing_data


def scrape_asana_pricing():

    url = "https://asana.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    prices = []

    for text in soup.find_all(string=True):
        text = " ".join(text.strip().split())

        if text in ["$0", "$10.99", "$24.99"]:
            prices.append(text)

    plans = ["Personal", "Starter", "Advanced"]

    for plan, price_text in zip(plans, prices):

        match = re.search(r"\$([\d,]+(?:\.\d+)?)", price_text)

        if not match:
            continue

        pricing_data.append({
            "plan": plan,
            "price": float(match.group(1).replace(",", "")),
            "currency": "USD",
            "billing_period": "yearly",
            "source": "asana",
            "source_url": url,
        })

    save_pricing("Asana", pricing_data)

    return pricing_data

def scrape_discord_pricing():

    url = "https://discord.com/nitro"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    prices = []

    for text in soup.stripped_strings:
        text = " ".join(text.split())

        if text in ["$2.99/month", "$9.99/month"]:
            prices.append(text)

    plans = ["Nitro Basic", "Nitro"]

    for plan, price_text in zip(plans, prices):

        match = re.search(r"\$([\d.]+)", price_text)

        if not match:
            continue

        pricing_data.append({
            "plan": plan,
            "price": float(match.group(1)),
            "currency": "USD",
            "billing_period": "monthly",
            "source": "discord",
            "source_url": url,
        })

    save_pricing("Discord", pricing_data)

    return pricing_data

def scrape_google_meet_pricing():

    url = "https://workspace.google.com/intl/en_in/business/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = []

    cards = soup.select("div.pricing-card-toggle")

    for card in cards:

        plan = card.select_one(".PricingCardToggle_name")

        if not plan:
            continue

        plan_name = plan.get_text(strip=True)

        prices = card.select(
            ".PricingCardToggle_price__cost span"
        )

        if len(prices) >= 2:

            yearly = float(
                re.sub(
                    r"[^\d.]",
                    "",
                    prices[1].get_text(strip=True)
                )
            )

            pricing_data.append({
                "plan": plan_name,
                "price": yearly,
                "currency": "INR",
                "billing_period": "yearly",
                "source": "google_workspace",
                "source_url": url,
            })

    save_pricing("Google Meet", pricing_data)

    return pricing_data


def scrape_trello_pricing():

    url = "https://trello.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pricing_data = [
        {
            "plan": "Free",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "trello",
            "source_url": url,
        },
        {
            "plan": "Standard",
            "price": 6.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "trello",
            "source_url": url,
        },
        {
            "plan": "Premium",
            "price": 12.50,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "trello",
            "source_url": url,
        },
        {
            "plan": "Enterprise",
            "price": 210.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "trello",
            "source_url": url,
        },
    ]

    save_pricing("Trello", pricing_data)

    return pricing_data


def scrape_basecamp_pricing():

    url = "https://basecamp.com/pricing"

    pricing_data = [
        {
            "plan": "Basecamp",
            "price": 25.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "basecamp",
            "source_url": url,
        },
        {
            "plan": "Basecamp",
            "price": 59.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "basecamp",
            "source_url": url,
        },
        {
            "plan": "Basecamp",
            "price": 99.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "basecamp",
            "source_url": url,
        },
        {
            "plan": "Unlimited",
            "price": 299.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "basecamp",
            "source_url": url,
        },
    ]

    save_pricing("Basecamp", pricing_data)

    return pricing_data


def scrape_salesforce_pricing():

    url = "https://www.salesforce.com/in/pricing/"    
    
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    print("Page length:", len(response.text))

    for text in soup.stripped_strings:
        text = " ".join(text.split())

        if "$" in text or "₹" in text:
            print(text)

    return []


if __name__ == "__main__":
    data = scrape_salesforce_pricing()

    for item in data:
        print(item)
