from fastapi import APIRouter, Query

from app.db import SessionLocal
from app.models.tool import Tool
from app.ml.overlap import jaccard_similarity, parse_features


router = APIRouter(
    prefix="/api/overlap",
    tags=["overlap"]
)


@router.get("")
def get_overlap(
    threshold: float = Query(
        default=0.0,
        ge=0.0,
        le=100.0
    )
):
    with SessionLocal() as session:
        tools = session.query(Tool).all()

        results = []

        for i in range(len(tools)):
            for j in range(i + 1, len(tools)):
                tool_a = tools[i]
                tool_b = tools[j]

                features_a = parse_features(tool_a.features)
                features_b = parse_features(tool_b.features)

                score = jaccard_similarity(features_a, features_b)
                similarity = round(score * 100, 2)

                if similarity >= threshold:
                    results.append({
                        "tool_a": tool_a.name,
                        "tool_b": tool_b.name,
                        "similarity": similarity
                    })

        return results