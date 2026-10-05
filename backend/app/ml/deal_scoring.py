def calculate_savings_percent(base_price, final_price):
    if base_price <= 0:
        return 0.0

    savings = ((base_price - final_price) / base_price) * 100
    return round(max(savings, 0.0), 2)


def calculate_feature_coverage(similarity_percent):
    return round(max(0.0, min(similarity_percent, 100.0)), 2)


def calculate_contract_score(contract_score):
    return round(max(0.0, min(contract_score, 100.0)), 2)


def calculate_deal_score(
    savings_percent,
    feature_coverage,
    contract_score
):
    score = (
        0.4 * savings_percent
        + 0.4 * feature_coverage
        + 0.2 * contract_score
    )

    return round(score, 2)