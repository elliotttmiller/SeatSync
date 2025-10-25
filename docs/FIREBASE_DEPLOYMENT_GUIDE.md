# Firebase Deployment Guide for SeatSync

Complete guide for deploying SeatSync to Google Firebase and Google Cloud Platform.

## Prerequisites

1. **Google Cloud Account**: Sign up at [console.cloud.google.com](https://console.cloud.google.com)
2. **Firebase Project**: Create at [console.firebase.google.com](https://console.firebase.google.com)
3. **Firebase CLI**: Already included in the Firebase Studio environment
4. **Google Cloud SDK**: Already included in the Firebase Studio environment

## Initial Setup

### 1. Firebase Project Configuration

```bash
# Login to Firebase (in Firebase Studio, this may already be done)
firebase login

# Initialize Firebase in the project (if not already done)
firebase init

# Select the following features:
# ✓ Firestore
# ✓ Functions
# ✓ Hosting
# ✓ Storage
# ✓ Emulators
```

### 2. Update Project ID

Edit `.firebaserc` and replace `seatsync-project` with your actual Firebase project ID:

```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

### 3. Environment Configuration

Create production environment file:

```bash
# Create production .env file
cp backend/.env.test .env.production

# Edit with production values
nano .env.production
```

Required production environment variables:

```bash
# Application
SECRET_KEY=<generate-strong-secret-key>
JWT_SECRET_KEY=<generate-strong-jwt-secret>
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Google Cloud
GOOGLE_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# API Keys (Production)
STUBHUB_API_KEY=your-production-key
SEATGEEK_CLIENT_ID=your-production-id
SEATGEEK_CLIENT_SECRET=your-production-secret
TICKETMASTER_API_KEY=your-production-key
OPENAI_API_KEY=your-production-key
ANTHROPIC_API_KEY=your-production-key
GEMINI_API_KEY=your-production-key

# CORS
CORS_ORIGIN=https://your-domain.com

# Database (Cloud SQL)
DB_HOST=/cloudsql/project:region:instance
DB_USER=seatsync
DB_PASSWORD=<strong-password>
DB_NAME=seatsync_prod
```

## Deployment Steps

### Step 1: Build Frontend

```bash
cd frontend
npm run build
cd ..
```

This creates an optimized production build in `frontend/build/`.

### Step 2: Deploy to Firebase Hosting

```bash
# Deploy frontend only
firebase deploy --only hosting:frontend

# Or deploy everything
firebase deploy
```

### Step 3: Deploy Backend to Cloud Run

#### Option A: Using Cloud Build

```bash
# Build and deploy in one command
gcloud run deploy seatsync-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars="$(cat .env.production | grep -v '^#' | xargs)"
```

#### Option B: Using Docker

```bash
# Build Docker image
docker build -t gcr.io/YOUR-PROJECT-ID/seatsync-backend ./backend

# Push to Google Container Registry
docker push gcr.io/YOUR-PROJECT-ID/seatsync-backend

# Deploy to Cloud Run
gcloud run deploy seatsync-backend \
  --image gcr.io/YOUR-PROJECT-ID/seatsync-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 4: Deploy Cloud Functions

```bash
# Deploy all functions
firebase deploy --only functions

# Or deploy specific function
firebase deploy --only functions:contextSummarizer
```

### Step 5: Set Up Cloud SQL (PostgreSQL)

```bash
# Create Cloud SQL instance
gcloud sql instances create seatsync-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create seatsync_prod \
  --instance=seatsync-db

# Create user
gcloud sql users create seatsync \
  --instance=seatsync-db \
  --password=<strong-password>

# Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com
```

### Step 6: Configure Cloud SQL Connection

Update Cloud Run service to connect to Cloud SQL:

```bash
gcloud run services update seatsync-backend \
  --add-cloudsql-instances PROJECT-ID:REGION:INSTANCE-NAME \
  --region us-central1
```

### Step 7: Run Database Migrations

```bash
# Connect to Cloud SQL instance
gcloud sql connect seatsync-db --user=seatsync

# Or run migrations from Cloud Shell
# First, set up Cloud SQL Proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# Then run migrations
alembic upgrade head
```

## Security Configuration

### 1. Firebase Security Rules

Security rules are already configured in:
- `firestore.rules` - Firestore database rules
- `storage.rules` - Cloud Storage rules
- `database.rules.json` - Realtime Database rules

Deploy security rules:

```bash
firebase deploy --only firestore:rules
firebase deploy --only storage:rules
firebase deploy --only database:rules
```

### 2. API Keys and Secrets

Use Google Secret Manager for production secrets:

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "your-jwt-key" | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member="serviceAccount:PROJECT-NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Update Cloud Run to use secrets:

```bash
gcloud run services update seatsync-backend \
  --update-secrets="SECRET_KEY=SECRET_KEY:latest" \
  --update-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest" \
  --region us-central1
```

### 3. CORS Configuration

Update CORS in `backend/app/main.py` for production domains.

### 4. Firebase App Check (Recommended)

Enable Firebase App Check for additional security:

1. Go to Firebase Console > App Check
2. Register your web app
3. Choose reCAPTCHA v3 or reCAPTCHA Enterprise
4. Update frontend to include App Check SDK

## Monitoring and Logging

### 1. Enable Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Or use Firebase Console
firebase logs:all
```

### 2. Set Up Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create \
  --display-name="SeatSync Backend Health" \
  --resource-type=uptime-url \
  --http-check-path="/health"
```

### 3. Configure Alerts

Set up alerts in Google Cloud Console for:
- High error rates
- High latency
- Resource exhaustion
- Security events

## Performance Optimization

### 1. Enable CDN for Static Assets

```bash
# Configure Cloud CDN for Cloud Run
gcloud compute backend-services update seatsync-backend \
  --enable-cdn \
  --global
```

### 2. Configure Caching

Update `firebase.json` hosting section with appropriate cache headers (already configured).

### 3. Enable Compression

Cloud Run automatically handles gzip compression for responses.

### 4. Set Up Cloud Storage for ML Models

```bash
# Create bucket for ML models
gsutil mb -l us-central1 gs://seatsync-ml-models

# Upload models
gsutil cp -r models/* gs://seatsync-ml-models/
```

## Continuous Deployment

### Set Up Cloud Build Triggers

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build frontend
  - name: 'node:20'
    entrypoint: npm
    args: ['install']
    dir: 'frontend'
  
  - name: 'node:20'
    entrypoint: npm
    args: ['run', 'build']
    dir: 'frontend'
  
  # Deploy frontend to Firebase
  - name: 'gcr.io/PROJECT-ID/firebase'
    args: ['deploy', '--only', 'hosting:frontend']
  
  # Build and deploy backend to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'seatsync-backend'
      - '--source=./backend'
      - '--platform=managed'
      - '--region=us-central1'
      - '--allow-unauthenticated'

timeout: 1200s
```

Connect to GitHub:

```bash
gcloud builds triggers create github \
  --repo-name=SeatSync \
  --repo-owner=elliotttmiller \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Cost Optimization

### 1. Set Resource Limits

```bash
# Update Cloud Run with cost-effective settings
gcloud run services update seatsync-backend \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --region us-central1
```

### 2. Enable Autoscaling

Cloud Run automatically scales down to zero when not in use.

### 3. Use Cloud Scheduler for Periodic Tasks

Instead of keeping instances running:

```bash
# Create a scheduled task
gcloud scheduler jobs create http scrape-data \
  --schedule="0 */6 * * *" \
  --uri="https://your-cloud-run-url/api/v1/intelligence/data-pipeline/start" \
  --http-method=POST
```

## Rollback Strategy

### Rollback Frontend

```bash
# List deployments
firebase hosting:rollback

# Rollback to specific version
firebase hosting:rollback --site frontend --version VERSION_ID
```

### Rollback Backend

```bash
# List revisions
gcloud run revisions list --service seatsync-backend --region us-central1

# Route traffic to previous revision
gcloud run services update-traffic seatsync-backend \
  --to-revisions=REVISION_NAME=100 \
  --region us-central1
```

## Testing in Production

### 1. Test Endpoints

```bash
# Health check
curl https://your-backend-url/health

# API test
curl -X POST https://your-backend-url/api/v1/predict-price \
  -H "Content-Type: application/json" \
  -d '{"eventId": "test", "section": "100", "row": "A"}'
```

### 2. Load Testing

Use Cloud Load Testing or Apache Bench:

```bash
ab -n 1000 -c 10 https://your-backend-url/health
```

## Troubleshooting

### Common Issues

1. **Cold Start Latency**: Increase min-instances or use Cloud Run always-on CPU allocation
2. **Database Connection Errors**: Check Cloud SQL proxy configuration
3. **CORS Errors**: Verify CORS_ORIGIN environment variable
4. **Out of Memory**: Increase memory allocation in Cloud Run
5. **Timeout Errors**: Increase timeout setting in Cloud Run

### Debug Commands

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=seatsync-backend" --limit 50 --format json

# Test Cloud SQL connection
gcloud sql connect seatsync-db --user=seatsync

# Check service status
gcloud run services describe seatsync-backend --region us-central1
```

## Maintenance

### Regular Updates

1. Update dependencies monthly
2. Review and rotate API keys quarterly
3. Review security rules quarterly
4. Monitor costs weekly
5. Update ML models as needed

### Backup Strategy

```bash
# Automated Firestore backups
gcloud firestore export gs://seatsync-backups/$(date +%Y%m%d)

# Cloud SQL automated backups (enabled by default)
# Configure in Cloud SQL instance settings
```

## Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Google Cloud Best Practices](https://cloud.google.com/architecture/framework)

## Support

For deployment issues:
- Firebase Support: [firebase.google.com/support](https://firebase.google.com/support)
- Google Cloud Support: [cloud.google.com/support](https://cloud.google.com/support)
- Community: [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)

---

**Last Updated**: October 2024
