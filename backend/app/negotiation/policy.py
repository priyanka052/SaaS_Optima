from typing import TypedDict


class VendorPolicy(TypedDict):
    max_discount_percent: float
    contract_score: float


DEFAULT_VENDOR_POLICY: VendorPolicy = {
    # Demo/configurable assumption.
    # This is NOT scraped data.
    "max_discount_percent": 10.0,

    # Demo/configurable assumption.
    # Replace with knowledge-base data when available.
    "contract_score": 70.0,
}


def calculate_vendor_min_price(
    base_price: float,
    max_discount_percent: float
) -> float:
    discount = base_price * (
        max_discount_percent / 100
    )

    return round(base_price - discount, 2)