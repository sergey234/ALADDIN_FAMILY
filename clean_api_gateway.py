#!/usr/bin/env python3
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/components/status/{component_id}")
async def get_component_status(component_id: str):
    return {
        "component_id": component_id,
        "status": "enabled",
        "message": "Mock response - SFM integration pending"
    }


