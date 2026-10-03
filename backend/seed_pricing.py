from datetime import datetime

from app.db import Base, SessionLocal, engine
from app.models.pricing import Pricing
from app.models.tool import Tool


# Make sure the pricing table exists
Base.metadata.create_all(bind=engine)


with SessionLocal() as session:
    slack = session.query(Tool).filter(Tool.name == "Slack").first()
    teams = session.query(Tool).filter(Tool.name == "Microsoft Teams").first()

    if slack:
        session.add(
            Pricing(
                tool_id=slack.id,
                plan="Demo Pro",
                price=750,
                currency="INR",
                billing_period="monthly",
                source="demo",
                source_url="https://slack.com/pricing",
                last_updated=datetime.utcnow(),
            )
        )

    if teams:
        session.add(
            Pricing(
                tool_id=teams.id,
                plan="Demo Business",
                price=300,
                currency="INR",
                billing_period="monthly",
                source="demo",
                source_url="https://www.microsoft.com/microsoft-teams",
                last_updated=datetime.utcnow(),
            )
        )

    session.commit()

print("Demo pricing records added!")