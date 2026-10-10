import csv

from app.ml.overlap import jaccard_similarity, parse_features


with open("data/tools.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    tools = list(reader)


for i in range(len(tools)):
    for j in range(i + 1, len(tools)):

        tool_a = tools[i]
        tool_b = tools[j]

        features_a = parse_features(tool_a["features"])
        features_b = parse_features(tool_b["features"])

        score = jaccard_similarity(features_a, features_b)

        print(
            f"{tool_a['name']} vs {tool_b['name']}: "
            f"{round(score * 100, 2)}%"
        )