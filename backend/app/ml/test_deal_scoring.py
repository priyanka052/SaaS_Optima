from app.ml.deal_scoring import (
    calculate_savings_percent,
    calculate_feature_coverage,
    calculate_contract_score,
    calculate_deal_score,
)


base_price = 294.75
final_price = 260.0

savings = calculate_savings_percent(
    base_price,
    final_price
)

features = calculate_feature_coverage(66.67)

contract = calculate_contract_score(80)

score = calculate_deal_score(
    savings,
    features,
    contract
)

print("Savings %:", savings)
print("Feature coverage:", features)
print("Contract score:", contract)
print("Overall deal score:", score)