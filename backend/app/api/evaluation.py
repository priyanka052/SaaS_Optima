
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.negotiation import Negotiation
from app.models.negotiation_turn import NegotiationTurn

router = APIRouter(
    prefix="/api/evaluation",
    tags=["Evaluation Metrics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def get_evaluation_summary(
    db: Session = Depends(get_db)
):
    """Calculate summary metrics from saved negotiations."""

    negotiations = db.query(Negotiation).all()
    turns = db.query(NegotiationTurn).all()

    total = len(negotiations)

    accepted = [
        item for item in negotiations
        if (item.status or "").lower() == "accepted"
    ]

    rejected = [
        item for item in negotiations
        if (item.status or "").lower() == "rejected"
    ]

    # Count the actions recorded for each negotiation.
    turn_counts = Counter(
        turn.negotiation_id for turn in turns
    )

    total_turns = len(turns)

    average_turns = (
        sum(turn_counts.get(item.id, 0) for item in negotiations)
        / total
        if total else 0.0
    )

    # Savings are averaged over accepted deals with a recorded value.
    savings_values = [
        float(item.savings_percent)
        for item in accepted
        if item.savings_percent is not None
    ]

    # Deal score is averaged across all negotiations with a score.
    score_values = [
        float(item.deal_score)
        for item in negotiations
        if item.deal_score is not None
    ]

    success_rate = (
        len(accepted) / total * 100
        if total else 0.0
    )

    status_breakdown = dict(
        Counter(
            (item.status or "unknown").lower()
            for item in negotiations
        )
    )

    return {
        "total_negotiations": total,
        "accepted_negotiations": len(accepted),
        "rejected_negotiations": len(rejected),
        "success_rate_percent": round(success_rate, 2),
        "average_savings_percent": (
            round(sum(savings_values) / len(savings_values), 2)
            if savings_values else None
        ),
        "average_deal_score": (
            round(sum(score_values) / len(score_values), 2)
            if score_values else None
        ),
        "total_turns": total_turns,
        "average_turns_per_negotiation": round(average_turns, 2),
        "status_breakdown": status_breakdown,
    }
