def jaccard_similarity(features_a, features_b):
    """
    Calculate Jaccard similarity between two feature lists.
    """

    set_a = set(features_a)
    set_b = set(features_b)

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def parse_features(feature_string):
    """
    Convert the semicolon-separated feature string
    from tools.csv into a list.
    """

    return [feature.strip() for feature in feature_string.split(";")]