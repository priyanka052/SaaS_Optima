from fastapi import FastAPI

from app.api import tools
from app.api import pricing
from app.api import overlap
from app.api import negotiation
from app.api import compare
from app.api import history
from app.api import email
from app.api import evaluation
from app.api import chat

from app.db import Base, engine
from app.models import pricing as pricing_model


Base.metadata.create_all(bind=engine)


app = FastAPI(title="SaaSOptima")

app.include_router(tools.router)
app.include_router(pricing.router)
app.include_router(overlap.router)
app.include_router(negotiation.router)
app.include_router(compare.router)
app.include_router(history.router)
app.include_router(email.router)
app.include_router(evaluation.router)
app.include_router(chat.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}