from pricing.updater import (
    scrape_slack_pricing,
    scrape_teams_pricing,
    scrape_zoom_pricing,
)

from pricing.generic import scrape_clickup_pricing


SCRAPERS = {
    "Slack": scrape_slack_pricing,
    "Microsoft Teams": scrape_teams_pricing,
    "Zoom": scrape_zoom_pricing,
    "ClickUp": scrape_clickup_pricing,
}


def run_all_scrapers():
    for tool_name, scraper in SCRAPERS.items():
        print(f"\nFetching pricing for {tool_name}...")

        try:
            pricing_data = scraper()

            print(f"Found {len(pricing_data)} pricing records.")

        except Exception as e:
            print(f"Failed for {tool_name}: {e}")

if __name__ == "__main__":
    run_all_scrapers()