from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter()

@router.post("/chat")
async def chat_with_gemini(payload: dict):
    # TODO: Implement async Gemini call
    return {"response": "dummy"} 