import requests
from app.db import SessionLocal
from app.models.tool import Tool


def inspect_websites():

    pricing_paths = [
        "/pricing",
        "/pricing/",
        "/plans",
        "/plans/",
        "/price",
    ]

    with SessionLocal() as session:
        tools = session.query(Tool).all()

        for tool in tools:

            print("\n" + "=" * 60)
            print(f"{tool.id}. {tool.name}")
            print("=" * 60)

            found = False

            for path in pricing_paths:

                url = tool.url.rstrip("/") + path

                try:
                    response = requests.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10,
                        allow_redirects=True
                    )

                    if response.status_code == 200:

                        text = response.text.lower()

                        if (
                            "pricing" in text
                            or "per month" in text
                            or "per user" in text
                            or "$" in text
                        ):
                            print("Possible pricing page:", response.url)
                            print("Status:", response.status_code)
                            print("Page size:", len(response.text))

                            found = True
                            break

                except Exception:
                    continue

            if not found:
                print("No obvious pricing page found")
if __name__ == "__main__":
    inspect_websites()