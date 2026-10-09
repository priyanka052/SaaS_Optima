from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

from app.db import Base


class NegotiationTurn(Base):
    __tablename__ = "negotiation_turns"

    id = Column(Integer, primary_key=True, index=True)

    negotiation_id = Column(
        Integer,
        ForeignKey("negotiations.id"),
        nullable=False
    )

    round_number = Column(Integer, nullable=False)

    agent = Column(String, nullable=False)
    action = Column(String, nullable=False)
    offer = Column(Float)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )