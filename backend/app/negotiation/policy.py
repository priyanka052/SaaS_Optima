from typing import TypedDict


class VendorPolicy(TypedDict):
    max_discount_percent: float
    contract_score: float


DEFAULT_VENDOR_POLICY: VendorPolicy = {
    "max_discount_percent": 10.0,
    "contract_score": 70.0,
}


def calculate_vendor_min_price(
    base_price: float,
    max_discount_percent: float
) -> float:
    discount = base_price * (max_discount_percent / 100)
    return round(base_price - discount, 2)


def calculate_buyer_opening_offer(
    base_price: float,
    buyer_budget: float
) -> float:
    return round(min(buyer_budget, base_price * 0.85), 2)


def calculate_vendor_counter_offer(
    base_price: float,
    vendor_min_price: float,
    round_number: int
) -> float:
    concession_factor = max(0.1, 0.5 - (round_number - 1) * 0.1)

    offer = vendor_min_price + (
        (base_price - vendor_min_price) * concession_factor
    )

    return round(max(vendor_min_price, offer), 2)