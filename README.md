# SeatSync Backend

## Overview
SeatSync is an AI-driven backend for ticket price prediction, context summarization, and conversational chat, powered by FastAPI, Gemini, and BigQuery.

## Setup
1. Clone the repo and install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with:
   - `GOOGLE_PROJECT_ID`
   - `GOOGLE_APPLICATION_CREDENTIALS`
   - `GEMINI_API_KEY`
   - `DATABASE_URL`
   - `SECRET_KEY`, `JWT_SECRET_KEY`
   - Any other required variables
3. Run database migrations:
   ```sh
   alembic upgrade head
   ```
4. Start the backend:
   ```sh
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Testing
Run all tests:
```sh
pytest -v -s
```

## Deployment
- Deploy to Railway or GCP as needed.
- For the Cloud Function, see `cloud_function/README.md`.

## API Endpoints
- `/health`: Health check
- `/api/v1/auth/login`: User login
- `/api/v1/auth/logout`: User logout
- `/api/v1/predict-price`: Predict ticket price (POST)
- `/api/v1/chat`: Conversational AI (POST)

## Cloud Function
- Summarizes news/social context and stores in BigQuery.
- Deploy and schedule with GCP Cloud Functions and Scheduler.

## Contributing
PRs welcome! See issues for roadmap and bugs. 