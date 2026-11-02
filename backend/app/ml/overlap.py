
import re


def normalize_feature(feature):
    """Normalize feature names before comparing them."""
    feature = str(feature).strip().lower()
    feature = re.sub(r"[-_/]+", " ", feature)
    feature = re.sub(r"\s+", " ", feature)
    return feature


def parse_features(feature_string):
    """Parse semicolon-separated features into unique normalized features."""
    if not feature_string:
        return []

    if isinstance(feature_string, (list, tuple, set)):
        values = feature_string
    else:
        values = feature_string.split(";")

    return sorted({
        normalize_feature(feature)
        for feature in values
        if normalize_feature(feature)
    })


def jaccard_similarity(features_a, features_b):
    """Calculate standard Jaccard similarity."""
    set_a = set(parse_features(features_a))
    set_b = set(parse_features(features_b))

    union = set_a | set_b

    if not union:
        return 0.0

    return len(set_a & set_b) / len(union)


def weighted_jaccard_similarity(
    features_a,
    features_b,
    feature_weights=None
):
    """
    Calculate weighted Jaccard similarity.

    Important features can receive higher weights.
    Features without specified weights receive weight 1.
    """
    set_a = set(parse_features(features_a))
    set_b = set(parse_features(features_b))

    union = set_a | set_b

    if not union:
        return 0.0

    weights = {
        normalize_feature(key): max(float(value), 0.0)
        for key, value in (feature_weights or {}).items()
    }

    intersection_weight = sum(
        weights.get(feature, 1.0)
        for feature in set_a & set_b
    )

    union_weight = sum(
        weights.get(feature, 1.0)
        for feature in union
    )

    if union_weight == 0:
        return 0.0

    return intersection_weight / union_weight


def compare_features(features_a, features_b, feature_weights=None):
    """Return similarity and common/unique feature details."""
    set_a = set(parse_features(features_a))
    set_b = set(parse_features(features_b))

    score = weighted_jaccard_similarity(
        set_a,
        set_b,
        feature_weights
    )

    return {
        "similarity": round(score * 100, 2),
        "common_features": sorted(set_a & set_b),
        "unique_features_a": sorted(set_a - set_b),
        "unique_features_b": sorted(set_b - set_a),
    }
