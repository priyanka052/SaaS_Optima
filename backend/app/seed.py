from pathlib import Path

import pandas as pd

from app.db import engine, Base, SessionLocal
from app.models.tool import Tool


# Find the data folder
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "tools.csv"


# Make sure the database table exists
Base.metadata.create_all(bind=engine)


# Read the CSV file
df = pd.read_csv(CSV_PATH)


# Open a database session
with SessionLocal() as session:

    for _, row in df.iterrows():

        # Check if this tool is already in the database
        existing_tool = (
            session.query(Tool)
            .filter(Tool.name == row["name"])
            .first()
        )

        # Don't insert the same tool twice
        if existing_tool:
            continue

        # Create a Tool object
        tool = Tool(
            name=row["name"],
            category=row["category"],
            url=row["url"],
            features=row["features"],
            price_inr=float(row["price_inr_per_user_month"])
        )

        # Add it to the database
        session.add(tool)

    # Save everything
    session.commit()


print("Tools successfully added to the database!")