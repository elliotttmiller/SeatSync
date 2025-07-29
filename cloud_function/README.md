# Cloud Function: Game Context Summarization

This function fetches upcoming games from BigQuery, gathers news/social context, calls Gemini for summarization, and updates the game_context_cache table in BigQuery.

## Deployment

1. Enable the required Google Cloud APIs:
   - BigQuery API
   - Cloud Functions API
   - Cloud Scheduler API
   - Generative Language API (Gemini)

2. Deploy the function:
   ```sh
   gcloud functions deploy summarize_game_context \
     --runtime python310 \
     --trigger-topic game-context-update \
     --entry-point main \
     --set-env-vars GOOGLE_PROJECT_ID=<your-gcp-project-id>,GEMINI_API_KEY=<your-gemini-api-key> \
     --service-account <your-service-account-email>
   ```

3. Set up Cloud Scheduler to publish to the `game-context-update` topic every hour.

## Configuration
- Set `GOOGLE_PROJECT_ID` and `GEMINI_API_KEY` as environment variables.
- The function expects a `games` table in your BigQuery dataset. 