from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
import httpx
import os
import asyncio
from google.cloud import bigquery
from google.oauth2 import service_account
from sqlalchemy import text

# NOTE: Replace 'your_dataset' with your actual BigQuery dataset name in the queries below.

router = APIRouter()

# Helper to run BigQuery in a thread pool (since google-cloud-bigquery is not async)
def run_bq_query(query):
    credentials = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    client = bigquery.Client(credentials=credentials, project=settings.GOOGLE_PROJECT_ID)
    return list(client.query(query).result())

@router.post("/predict-price")
async def predict_price(ticket: dict, db: AsyncSession = Depends(get_db)):
    # 1. Fetch context from BigQuery
    game_id = ticket.get("game_id")
    context_query = f"""
        SELECT context_summary FROM `{settings.GOOGLE_PROJECT_ID}.your_dataset.game_context_cache`
        WHERE game_id = '{game_id}'
        ORDER BY last_updated DESC LIMIT 1
    """
    loop = asyncio.get_event_loop()
    context_rows = await loop.run_in_executor(None, run_bq_query, context_query)
    context = context_rows[0]["context_summary"] if context_rows else ""

    # 2. Fetch few-shot examples
    examples_query = f"""
        SELECT prompt, completion FROM `{settings.GOOGLE_PROJECT_ID}.your_dataset.price_prediction_examples`
        WHERE game_id = '{game_id}'
        LIMIT 3
    """
    examples_rows = await loop.run_in_executor(None, run_bq_query, examples_query)
    examples = "\n".join([f"Q: {row['prompt']}\nA: {row['completion']}" for row in examples_rows])

    # 3. Build Gemini prompt
    prompt = f"""
Context:
{context}

Examples:
{examples}

Now, given the following ticket info, predict the optimal price:
{ticket}

Respond with only the price as a number.
"""

    # 4. Call Gemini API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers={"Authorization": f"Bearer {settings.GEMINI_API_KEY}"},
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )
        response.raise_for_status()
        gemini_result = response.json()

    # 5. Parse price from Gemini response
    try:
        price_text = gemini_result["candidates"][0]["content"]["parts"][0]["text"]
        price = float(price_text.strip().replace("$", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse price: {e}")

    return {"reasoning": prompt, "price": price} 