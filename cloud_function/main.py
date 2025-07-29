import os
from google.cloud import bigquery
from datetime import datetime, timedelta
import requests

PROJECT = os.environ["GOOGLE_PROJECT_ID"]
DATASET = "your_dataset"  # TODO: Replace with your dataset name
CONTEXT_TABLE = f"{PROJECT}.{DATASET}.game_context_cache"
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]


def get_upcoming_games():
    bq_client = bigquery.Client()
    query = f"""
        SELECT game_id, game_date
        FROM `{PROJECT}.{DATASET}.games`
        WHERE game_date BETWEEN CURRENT_DATE() AND DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY)
    """
    return bq_client.query(query).result()


def fetch_news_and_social(game):
    # Placeholder: Implement your news/social API calls here
    return ["Example article about the game..."]


def summarize_with_gemini(game, articles):
    prompt = f"Summarize the following articles for {game['game_id']} on {game['game_date']}:\n" + "\n".join(articles)
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def update_context_cache(game, summary):
    bq_client = bigquery.Client()
    row = {
        "game_id": game["game_id"],
        "game_date": game["game_date"],
        "last_updated": datetime.utcnow().isoformat(),
        "context_summary": summary
    }
    errors = bq_client.insert_rows_json(CONTEXT_TABLE, [row])
    if errors:
        print(f"BigQuery insert errors: {errors}")


def main(event, context):
    for game in get_upcoming_games():
        articles = fetch_news_and_social(game)
        summary = summarize_with_gemini(game, articles)
        update_context_cache(game, summary) 