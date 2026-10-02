from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

from app.db import Base


class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)

    plan = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    billing_period = Column(String, nullable=False, default="monthly")

    source = Column(String, nullable=False)
    source_url = Column(String)

    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)