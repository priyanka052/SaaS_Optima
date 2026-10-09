from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.negotiation import Negotiation
from app.models.negotiation_turn import NegotiationTurn

router = APIRouter(
    prefix="/api/history",
    tags=["History & Audit Trail"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_negotiation(item):
    return {
        "negotiation_id": item.id,
        "tool_name": item.tool_name,
        "base_price": item.base_price,
        "buyer_budget": item.buyer_budget,
        "final_price": item.final_price,
        "status": item.status,
        "savings_percent": item.savings_percent,
        "feature_coverage": item.feature_coverage,
        "contract_score": item.contract_score,
        "deal_score": item.deal_score,
        "created_at": (
            item.created_at.isoformat()
            if item.created_at else None
        ),
        "completed_at": (
            item.completed_at.isoformat()
            if item.completed_at else None
        ),
    }


@router.get("")
def get_negotiation_history(
    db: Session = Depends(get_db)
):
    """Return a summary of all saved negotiations."""
    negotiations = (
        db.query(Negotiation)
        .order_by(Negotiation.created_at.desc())
        .all()
    )

    return {
        "total": len(negotiations),
        "negotiations": [
            serialize_negotiation(item)
            for item in negotiations
        ],
    }


@router.get("/{negotiation_id}")
def get_negotiation_audit_trail(
    negotiation_id: int,
    db: Session = Depends(get_db)
):
    """Return one negotiation and its chronological agent actions."""
    negotiation = (
        db.query(Negotiation)
        .filter(Negotiation.id == negotiation_id)
        .first()
    )

    if negotiation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Negotiation {negotiation_id} not found"
        )

    turns = (
        db.query(NegotiationTurn)
        .filter(
            NegotiationTurn.negotiation_id == negotiation_id
        )
        .order_by(
            NegotiationTurn.round_number.asc(),
            NegotiationTurn.id.asc()
        )
        .all()
    )

    audit_trail = [
        {
            "turn_id": turn.id,
            "round_number": turn.round_number,
            "agent": turn.agent,
            "action": turn.action,
            "offer": turn.offer,
            "created_at": (
                turn.created_at.isoformat()
                if turn.created_at else None
            ),
        }
        for turn in turns
    ]

    return {
        "negotiation": serialize_negotiation(negotiation),
        "audit_trail": audit_trail,
        "total_turns": len(audit_trail),
    }