from fastapi import APIRouter

from app.db import SessionLocal
from app.models.tool import Tool


router = APIRouter(
    prefix="/api/tools",
    tags=["tools"]
)


@router.get("")
def get_tools():
    with SessionLocal() as session:
        tools = session.query(Tool).all()

        return [
            {
                "id": tool.id,
                "name": tool.name,
                "category": tool.category,
                "url": tool.url,
                "features": tool.features.split(";"),
                "price_inr": tool.price_inr
            }
            for tool in tools
        ]