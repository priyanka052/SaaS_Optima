from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.db import Base


class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(Integer, primary_key=True, index=True)

    tool_name = Column(String, nullable=False)

    base_price = Column(Float, nullable=False)
    buyer_budget = Column(Float, nullable=False)

    final_price = Column(Float)

    status = Column(String, nullable=False)

    savings_percent = Column(Float, nullable=False, default=0.0)
    feature_coverage = Column(Float, nullable=False, default=0.0)
    contract_score = Column(Float, nullable=False, default=0.0)
    deal_score = Column(Float, nullable=False, default=0.0)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = Column(DateTime)