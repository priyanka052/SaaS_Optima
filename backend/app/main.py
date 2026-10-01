from fastapi import FastAPI

from app.api import tools


app = FastAPI(title="SaaSOptima")


app.include_router(tools.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}