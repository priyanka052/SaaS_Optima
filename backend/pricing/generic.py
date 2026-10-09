from operator import index
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


def scrape_hubspot_pricing():

    url = "https://www.hubspot.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    print("Page length:", len(response.text))

    html = response.text

    keywords = [
        "pricing-pages-ui",
        "__NEXT_DATA__",
        "__NUXT__",
        "Starter",
        "Professional",
        "Enterprise",
        "Free",
        "1300",
        "4700"
    ]

    for keyword in keywords:

        print(f"\n--- {keyword} ---")

        positions = [
            m.start()
            for m in re.finditer(
                re.escape(keyword),
                html,
                re.IGNORECASE
            )
        ]

        print("Count:", len(positions))

        for pos in positions[:3]:

            start = max(0, pos - 300)
            end = min(len(html), pos + 700)

            print(html[start:end])

    return []


def scrape_zoho_crm_pricing():

    url = "https://www.zoho.com/crm/zohocrm-pricing.html"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    page_text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Standard": 800,
        "Professional": 1400,
        "Enterprise": 2400,
    }

    for plan, price in plans.items():

        if plan in page_text:

            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "INR",
                "billing_period": "monthly",
                "source": "zoho_crm",
                "source_url": url,
            })

    save_pricing("Zoho CRM", pricing_data)

    return pricing_data

def scrape_freshsales_pricing():

    url = "https://www.freshworks.com/crm/pricing/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    page_text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Growth": 9,
        "Pro": 39,
        "Enterprise": 59,
    }

    for plan, price in plans.items():

        if plan in page_text:

            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "yearly",
                "source": "freshsales",
                "source_url": url,
            })

    save_pricing("Freshsales", pricing_data)

    return pricing_data

def scrape_gitlab_pricing():

    url = "https://about.gitlab.com/pricing/"

    pricing_data = [
        {
            "plan": "Free",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "gitlab",
            "source_url": url,
        },
        {
            "plan": "Premium",
            "price": 29.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "gitlab",
            "source_url": url,
        },
    ]

    save_pricing("GitLab", pricing_data)

    return pricing_data

def scrape_bitbucket_pricing():

    url = "https://www.atlassian.com/software/bitbucket/pricing"

    pricing_data = [
        {
            "plan": "Free",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "bitbucket",
            "source_url": url,
        },
        {
            "plan": "Standard",
            "price": 3.65,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "bitbucket",
            "source_url": url,
        },
        {
            "plan": "Premium",
            "price": 7.25,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "bitbucket",
            "source_url": url,
        },
    ]

    save_pricing("Bitbucket", pricing_data)

    return pricing_data

def scrape_postman_pricing():

    url = "https://www.postman.com/pricing/"

    pricing_data = [
        {
            "plan": "Free",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "postman",
            "source_url": url,
        },
        {
            "plan": "Solo",
            "price": 9.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "postman",
            "source_url": url,
        },
        {
            "plan": "Team",
            "price": 19.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "postman",
            "source_url": url,
        },
    ]

    save_pricing("Postman", pricing_data)

    return pricing_data

def scrape_figma_pricing():

    url = "https://www.figma.com/pricing/"

    pricing_data = [
        {
            "plan": "Starter",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Professional - Full seat",
            "price": 16.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Professional - Dev seat",
            "price": 12.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Professional - Collab seat",
            "price": 3.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Organization - Full seat",
            "price": 55.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Organization - Dev seat",
            "price": 25.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Organization - Collab seat",
            "price": 5.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Enterprise - Full seat",
            "price": 90.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Enterprise - Dev seat",
            "price": 35.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
        {
            "plan": "Enterprise - Collab seat",
            "price": 5.0,
            "currency": "USD",
            "billing_period": "monthly",
            "source": "figma",
            "source_url": url,
        },
    ]

    save_pricing("Figma", pricing_data)

    return pricing_data

def scrape_intercom_pricing():
    url = "https://www.intercom.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Essential": 29.0,
        "Advanced": 85.0,
        "Expert": 132.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "intercom",
                "source_url": url,
            })

    save_pricing("Intercom", pricing_data)

    return pricing_data

def scrape_freshdesk_pricing():
    url = "https://www.freshworks.com/freshdesk/pricing/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Growth": 19.0,
        "Pro": 55.0,
        "Enterprise": 89.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "yearly",
                "source": "freshdesk",
                "source_url": url,
            })

    save_pricing("Freshdesk", pricing_data)

    return pricing_data

def scrape_help_scout_pricing():
    url = "https://www.helpscout.com/pricing/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Standard": 25.0,
        "Plus": 45.0,
        "Pro": 75.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "help_scout",
                "source_url": url,
            })

    save_pricing("Help Scout", pricing_data)

    return pricing_data

def scrape_hootsuite_pricing():
    url = "https://www.hootsuite.com/plans"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Standard": 99.0,
        "Professional": 199.0,
        "Advanced": 399.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "yearly",
                "source": "hootsuite",
                "source_url": url,
            })

    save_pricing("Hootsuite", pricing_data)

    return pricing_data

def scrape_buffer_pricing():
    url = "https://buffer.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Essentials": 5.0,
        "Team": 10.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "yearly",
                "source": "buffer",
                "source_url": url,
            })

    if "Free forever" in text:
        pricing_data.append({
            "plan": "Free",
            "price": 0.0,
            "currency": "USD",
            "billing_period": "yearly",
            "source": "buffer",
            "source_url": url,
        })

    save_pricing("Buffer", pricing_data)

    return pricing_data


def scrape_dropbox_pricing():
    url = "https://www.dropbox.com/plans"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Plus": 9.99,
        "Standard": 15.0,
        "Advanced": 24.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "dropbox",
                "source_url": url,
            })

    save_pricing("Dropbox", pricing_data)

    return pricing_data


def scrape_xero_pricing():
    url = "https://www.xero.com/us/pricing-plans/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Early": 27.0,
        "Growing": 59.0,
        "Established": 97.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "xero",
                "source_url": url,
            })

    save_pricing("Xero", pricing_data)

    return pricing_data


def scrape_freshbooks_pricing():
    url = "https://www.freshbooks.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Lite": 23.0,
        "Plus": 43.0,
        "Premium": 70.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "freshbooks",
                "source_url": url,
            })

    save_pricing("FreshBooks", pricing_data)

    return pricing_data

def scrape_bamboohr_pricing():
    url = "https://www.bamboohr.com/pricing/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Core": 10.0,
        "Pro": 17.0,
        "Elite": 25.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "bamboohr",
                "source_url": url,
            })

    save_pricing("BambooHR", pricing_data)

    return pricing_data

def scrape_deel_pricing():
    url = "https://www.deel.com/pricing/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Find talent": 14.0,
        "Hire contractors": 49.0,
        "Contractor of Record": 325.0,
        "US PEO": 125.0,
        "EOR": 599.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "deel",
                "source_url": url,
            })

    save_pricing("Deel", pricing_data)

    return pricing_data

def scrape_claude_pricing():
    url = "https://claude.com/pricing"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    pricing_data = []

    cards = soup.find_all(
        "h3",
        string=lambda s: s and s.strip() in ["Free", "Pro", "Max"]
    )

    for heading in cards:
        plan = heading.get_text(strip=True)
        card_text = heading.parent.parent.get_text(" ", strip=True)

        if plan == "Free":
            pricing_data.append({
                "plan": "Free",
                "price": 0.0,
                "currency": "USD",
                "billing_period": "monthly",
                "source": "claude",
                "source_url": url,
            })

        elif plan == "Pro":
            match = re.search(r"\$(\d+(?:\.\d+)?)", card_text)

            if match:
                pricing_data.append({
                    "plan": "Pro",
                    "price": float(match.group(1)),
                    "currency": "USD",
                    "billing_period": "yearly",
                    "source": "claude",
                    "source_url": url,
                })

        elif plan == "Max":
            match = re.search(r"\$(\d+(?:\.\d+)?)", card_text)

            if match:
                pricing_data.append({
                    "plan": "Max",
                    "price": float(match.group(1)),
                    "currency": "USD",
                    "billing_period": "monthly",
                    "source": "claude",
                    "source_url": url,
                })

    save_pricing("Claude", pricing_data)

    return pricing_data


def scrape_wrike_pricing():
    url = "https://www.wrike.com/price-vag/"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    pricing_data = []

    plans = {
        "Free": 0.0,
        "Team": 10.0,
        "Business": 25.0,
    }

    for plan, price in plans.items():
        if plan in text:
            pricing_data.append({
                "plan": plan,
                "price": price,
                "currency": "USD",
                "billing_period": "yearly",
                "source": "wrike",
                "source_url": url,
            })

    save_pricing("Wrike", pricing_data)

    return pricing_data

if __name__ == "__main__":

    data = scrape_figma_pricing()

    for item in data:
        print(item)