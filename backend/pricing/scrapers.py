from pricing.updater import (
    scrape_slack_pricing,
    scrape_teams_pricing,
    scrape_zoom_pricing,
)


from pricing.generic import (
    scrape_asana_pricing,
    scrape_bamboohr_pricing,
    scrape_basecamp_pricing,
    scrape_bitbucket_pricing,
    scrape_buffer_pricing,
    scrape_claude_pricing,
    scrape_clickup_pricing,
    scrape_deel_pricing,
    scrape_discord_pricing,
    scrape_dropbox_pricing,
    scrape_figma_pricing,
    scrape_freshbooks_pricing,
    scrape_freshdesk_pricing,
    scrape_freshsales_pricing,
    scrape_gitlab_pricing,
    scrape_google_meet_pricing,
    scrape_help_scout_pricing,
    scrape_hootsuite_pricing,
    scrape_intercom_pricing,
    scrape_monday_pricing,
    scrape_postman_pricing,
    scrape_trello_pricing,
    scrape_wrike_pricing,
    scrape_xero_pricing,
    scrape_zoho_crm_pricing,
    
)


from pricing.generic import scrape_freshdesk_pricing
from pricing.generic import scrape_clickup_pricing
from pricing.generic import scrape_help_scout_pricing
from pricing.generic import scrape_hootsuite_pricing
from pricing.generic import scrape_buffer_pricing
from pricing.generic import scrape_dropbox_pricing
from pricing.generic import scrape_xero_pricing
from pricing.generic import scrape_freshbooks_pricing
from pricing.generic import scrape_bamboohr_pricing
from pricing.generic import scrape_deel_pricing
from pricing.generic import scrape_claude_pricing
from pricing.generic import scrape_wrike_pricing


SCRAPERS = {
    "Slack": scrape_slack_pricing,
    "Microsoft Teams": scrape_teams_pricing,
    "Zoom": scrape_zoom_pricing,
    "Asana": scrape_asana_pricing,
    "BambooHR": scrape_bamboohr_pricing,
    "Basecamp": scrape_basecamp_pricing,
    "Bitbucket": scrape_bitbucket_pricing,
    "Buffer": scrape_buffer_pricing,
    "Claude": scrape_claude_pricing,
    "ClickUp": scrape_clickup_pricing,
    "Deel": scrape_deel_pricing,
    "Discord": scrape_discord_pricing,
    "Dropbox": scrape_dropbox_pricing,
    "Figma": scrape_figma_pricing,
    "FreshBooks": scrape_freshbooks_pricing,
    "Freshdesk": scrape_freshdesk_pricing,
    "Freshsales": scrape_freshsales_pricing,
    "GitLab": scrape_gitlab_pricing,
    "Google Meet": scrape_google_meet_pricing,
    "Help Scout": scrape_help_scout_pricing,
    "Hootsuite": scrape_hootsuite_pricing,
    "Intercom": scrape_intercom_pricing,
    "Monday.com": scrape_monday_pricing,
    "Postman": scrape_postman_pricing,
    "Trello": scrape_trello_pricing,
    "Wrike": scrape_wrike_pricing,
    "Xero": scrape_xero_pricing,
    "Zoho CRM": scrape_zoho_crm_pricing,

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