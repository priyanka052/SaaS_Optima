import sys

sys.path.insert(0, "backend")

from app.db import SessionLocal
from app.models.tool import Tool


TOOLS = [
    # Communication
    {
        "name": "Slack",
        "category": "Communication",
        "url": "https://slack.com",
        "features": "chat;channels;video calls;file sharing;integrations",
    },
    {
        "name": "Microsoft Teams",
        "category": "Communication",
        "url": "https://www.microsoft.com/microsoft-teams",
        "features": "chat;channels;video calls;file sharing;collaboration",
    },
    {
        "name": "Zoom",
        "category": "Communication",
        "url": "https://zoom.us",
        "features": "video meetings;chat;webinars;screen sharing",
    },
    {
        "name": "Discord",
        "category": "Communication",
        "url": "https://discord.com",
        "features": "chat;voice;video;communities;screen sharing",
    },
    {
        "name": "Google Meet",
        "category": "Communication",
        "url": "https://meet.google.com",
        "features": "video meetings;screen sharing;chat;recording",
    },

    # Project Management
    {
        "name": "Jira",
        "category": "Project Management",
        "url": "https://www.atlassian.com/software/jira",
        "features": "issue tracking;agile boards;roadmaps;reports",
    },
    {
        "name": "Asana",
        "category": "Project Management",
        "url": "https://asana.com",
        "features": "tasks;projects;workflows;timeline;automation",
    },
    {
        "name": "Trello",
        "category": "Project Management",
        "url": "https://trello.com",
        "features": "boards;cards;tasks;automation;collaboration",
    },
    {
        "name": "ClickUp",
        "category": "Project Management",
        "url": "https://clickup.com",
        "features": "tasks;docs;goals;dashboards;automation",
    },
    {
        "name": "Monday.com",
        "category": "Project Management",
        "url": "https://monday.com",
        "features": "work management;projects;dashboards;automation",
    },
    {
        "name": "Basecamp",
        "category": "Project Management",
        "url": "https://basecamp.com",
        "features": "projects;tasks;messaging;scheduling;files",
    },

    # CRM
    {
        "name": "Salesforce",
        "category": "CRM",
        "url": "https://www.salesforce.com",
        "features": "CRM;sales;marketing;analytics;automation",
    },
    {
        "name": "HubSpot",
        "category": "CRM",
        "url": "https://www.hubspot.com",
        "features": "CRM;marketing;sales;service;automation",
    },
    {
        "name": "Zoho CRM",
        "category": "CRM",
        "url": "https://www.zoho.com/crm",
        "features": "CRM;sales;automation;analytics;lead management",
    },
    {
        "name": "Pipedrive",
        "category": "CRM",
        "url": "https://www.pipedrive.com",
        "features": "sales pipeline;leads;automation;reports",
    },
    {
        "name": "Freshsales",
        "category": "CRM",
        "url": "https://www.freshworks.com/crm",
        "features": "CRM;leads;email;automation;analytics",
    },

    # Development
    {
        "name": "GitHub",
        "category": "Development",
        "url": "https://github.com",
        "features": "repositories;git;issues;actions;collaboration",
    },
    {
        "name": "GitLab",
        "category": "Development",
        "url": "https://gitlab.com",
        "features": "repositories;CI/CD;issues;security;planning",
    },
    {
        "name": "Bitbucket",
        "category": "Development",
        "url": "https://bitbucket.org",
        "features": "git;repositories;CI/CD;code review",
    },
    {
        "name": "Postman",
        "category": "Development",
        "url": "https://www.postman.com",
        "features": "API testing;API documentation;collections;automation",
    },
    {
        "name": "JetBrains",
        "category": "Development",
        "url": "https://www.jetbrains.com",
        "features": "IDEs;development tools;code analysis;team tools",
    },

    # Design
    {
        "name": "Figma",
        "category": "Design",
        "url": "https://www.figma.com",
        "features": "UI design;prototyping;collaboration;design systems",
    },
    {
        "name": "Canva",
        "category": "Design",
        "url": "https://www.canva.com",
        "features": "graphic design;templates;presentations;collaboration",
    },
    {
        "name": "Adobe Creative Cloud",
        "category": "Design",
        "url": "https://www.adobe.com/creativecloud.html",
        "features": "Photoshop;Illustrator;Premiere Pro;design tools",
    },
    {
        "name": "Miro",
        "category": "Design",
        "url": "https://miro.com",
        "features": "whiteboards;brainstorming;workshops;collaboration",
    },

    # Productivity
    {
        "name": "Notion",
        "category": "Productivity",
        "url": "https://www.notion.so",
        "features": "documents;databases;wiki;tasks;AI",
    },
    {
        "name": "Evernote",
        "category": "Productivity",
        "url": "https://evernote.com",
        "features": "notes;documents;tasks;web clipping",
    },
    {
        "name": "Airtable",
        "category": "Productivity",
        "url": "https://www.airtable.com",
        "features": "databases;spreadsheets;automation;interfaces",
    },
    {
        "name": "Coda",
        "category": "Productivity",
        "url": "https://coda.io",
        "features": "documents;tables;automation;collaboration",
    },
    {
        "name": "Google Workspace",
        "category": "Productivity",
        "url": "https://workspace.google.com",
        "features": "Gmail;Drive;Docs;Sheets;Meet",
    },

    # Customer Support
    {
        "name": "Zendesk",
        "category": "Customer Support",
        "url": "https://www.zendesk.com",
        "features": "ticketing;live chat;knowledge base;analytics",
    },
    {
        "name": "Intercom",
        "category": "Customer Support",
        "url": "https://www.intercom.com",
        "features": "messaging;chatbots;support;knowledge base",
    },
    {
        "name": "Freshdesk",
        "category": "Customer Support",
        "url": "https://www.freshworks.com/freshdesk",
        "features": "ticketing;knowledge base;automation;analytics",
    },
    {
        "name": "Help Scout",
        "category": "Customer Support",
        "url": "https://www.helpscout.com",
        "features": "help desk;email;knowledge base;customer management",
    },

    # Marketing
    {
        "name": "Mailchimp",
        "category": "Marketing",
        "url": "https://mailchimp.com",
        "features": "email marketing;automation;audience management;analytics",
    },
    {
        "name": "Semrush",
        "category": "Marketing",
        "url": "https://www.semrush.com",
        "features": "SEO;keyword research;competitor analysis;marketing",
    },
    {
        "name": "Ahrefs",
        "category": "Marketing",
        "url": "https://ahrefs.com",
        "features": "SEO;backlinks;keyword research;site audit",
    },
    {
        "name": "Hootsuite",
        "category": "Marketing",
        "url": "https://www.hootsuite.com",
        "features": "social media management;scheduling;analytics",
    },
    {
        "name": "Buffer",
        "category": "Marketing",
        "url": "https://buffer.com",
        "features": "social scheduling;publishing;analytics",
    },

    # Storage
    {
        "name": "Dropbox",
        "category": "Storage",
        "url": "https://www.dropbox.com",
        "features": "cloud storage;file sharing;collaboration;backup",
    },
    {
        "name": "Box",
        "category": "Storage",
        "url": "https://www.box.com",
        "features": "cloud storage;file sharing;security;collaboration",
    },
    {
        "name": "OneDrive",
        "category": "Storage",
        "url": "https://www.microsoft.com/microsoft-365/onedrive",
        "features": "cloud storage;file sharing;backup;collaboration",
    },

    # Accounting / Finance
    {
        "name": "QuickBooks",
        "category": "Accounting",
        "url": "https://quickbooks.intuit.com",
        "features": "accounting;invoicing;expenses;payroll;reports",
    },
    {
        "name": "Xero",
        "category": "Accounting",
        "url": "https://www.xero.com",
        "features": "accounting;invoicing;expenses;bank reconciliation",
    },
    {
        "name": "FreshBooks",
        "category": "Accounting",
        "url": "https://www.freshbooks.com",
        "features": "invoicing;expenses;accounting;time tracking",
    },

    # HR
    {
        "name": "BambooHR",
        "category": "HR",
        "url": "https://www.bamboohr.com",
        "features": "HR;employee records;payroll;performance",
    },
    {
        "name": "Gusto",
        "category": "HR",
        "url": "https://gusto.com",
        "features": "payroll;benefits;HR;employee management",
    },
    {
        "name": "Deel",
        "category": "HR",
        "url": "https://www.deel.com",
        "features": "global payroll;contractors;HR;compliance",
    },

    # AI
    {
        "name": "ChatGPT",
        "category": "AI",
        "url": "https://chatgpt.com",
        "features": "AI assistant;chat;writing;coding;analysis",
    },
    {
        "name": "Claude",
        "category": "AI",
        "url": "https://claude.ai",
        "features": "AI assistant;writing;analysis;coding",
    },
    {
        "name": "Google Gemini",
        "category": "AI",
        "url": "https://gemini.google.com",
        "features": "AI assistant;chat;writing;analysis",
    },
    {
        "name": "Perplexity",
        "category": "AI",
        "url": "https://www.perplexity.ai",
        "features": "AI search;research;answers;citations",
    },

    # Collaboration
    {
        "name": "Confluence",
        "category": "Collaboration",
        "url": "https://www.atlassian.com/software/confluence",
        "features": "wiki;documentation;knowledge management;collaboration",
    },
    {
        "name": "Wrike",
        "category": "Collaboration",
        "url": "https://www.wrike.com",
        "features": "project management;workflows;collaboration;reports",
    },
]


def seed_tools():
    with SessionLocal() as session:
        added = 0
        skipped = 0

        for data in TOOLS:
            existing = (
                session.query(Tool)
                .filter(Tool.name == data["name"])
                .first()
            )

            if existing:
                skipped += 1
                continue

            tool = Tool(
                name=data["name"],
                category=data["category"],
                url=data["url"],
                features=data["features"],
                price_inr=None,
            )

            session.add(tool)
            added += 1

        session.commit()

        print(f"Tools added: {added}")
        print(f"Tools already present: {skipped}")
        print(f"Total tools in database: {session.query(Tool).count()}")


if __name__ == "__main__":
    seed_tools()