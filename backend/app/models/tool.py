from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    url = Column(String)
    features = Column(String, nullable=False)
    price_inr = Column(Float)