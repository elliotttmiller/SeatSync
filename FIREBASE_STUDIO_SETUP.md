# Firebase Studio Setup Guide for SeatSync

This document provides comprehensive instructions for configuring and using SeatSync with Firebase Studio (formerly Project IDX).

## Overview

Firebase Studio is a cloud-based development environment that provides a complete, preconfigured workspace for full-stack development. This setup includes:

- **Python 3.11** environment for FastAPI backend
- **Node.js 20** for React frontend
- **PostgreSQL 15** database service
- **Firebase Tools** for deployment
- **Google Cloud SDK** for cloud integration
- Complete development toolchain with IDE extensions

## Configuration Files

### `.idx/dev.nix`

The main configuration file that defines the development environment using Nix package manager. It includes:

1. **Packages**: All necessary system packages and tools
2. **Environment Variables**: Development environment settings
3. **IDE Extensions**: VS Code extensions for enhanced development experience
4. **Workspace Lifecycle Hooks**: Automated setup and startup tasks
5. **Preview Configuration**: Multi-service preview setup
6. **Services**: Database and cache services

## Getting Started

### 1. Open in Firebase Studio

1. Navigate to [Firebase Studio](https://idx.google.com/)
2. Sign in with your Google account
3. Import this repository from GitHub
4. Firebase Studio will automatically detect and apply the `.idx/dev.nix` configuration

### 2. Automatic Setup

When you first open the workspace, Firebase Studio will automatically:

1. Install all Nix packages defined in `dev.nix`
2. Create a Python virtual environment (`.venv`)
3. Install Python dependencies from `backend/requirements.txt`
4. Install Node.js dependencies from `frontend/package.json`
5. Run database migrations with Alembic
6. Install Scrapling browser automation tools

This process may take 5-10 minutes on first launch.

### 3. Environment Variables

Create a `.env` file in the root directory with your actual API keys and secrets:

```bash
# Copy from template
cp backend/.env.test .env

# Edit with your actual values
SECRET_KEY=your-actual-secret-key
JWT_SECRET_KEY=your-actual-jwt-secret
DATABASE_URL=postgresql://user:password@localhost:5432/seatsync

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_API_KEY=your-firebase-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Optional API Keys
STUBHUB_API_KEY=your-stubhub-key
SEATGEEK_CLIENT_ID=your-seatgeek-id
TICKETMASTER_API_KEY=your-ticketmaster-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key
```

### 4. Running the Application

Firebase Studio provides three preview environments:

#### Backend API (Port 8000)
```bash
# Automatically starts with the "backend" preview
# Access at: https://8000-[your-workspace-url]
```

#### Frontend React App (Port 3000)
```bash
# Automatically starts with the "frontend" preview
# Access at: https://3000-[your-workspace-url]
```

#### Streamlit Dashboard (Port 8501)
```bash
# Optionally start with the "streamlit" preview
# Access at: https://8501-[your-workspace-url]
```

### 5. Manual Commands

If you need to run commands manually:

```bash
# Activate Python virtual environment
source .venv/bin/activate

# Run backend
cd backend
uvicorn app.main:app --reload

# Run frontend (in a new terminal)
cd frontend
npm start

# Run Streamlit dashboard
streamlit run streamlit_app.py

# Run tests
pytest -v

# Database migrations
alembic upgrade head
```

## Development Workflow

### Making Code Changes

1. Edit files in the IDE
2. Changes are automatically watched and reloaded
3. Backend: FastAPI auto-reloads on code changes
4. Frontend: React hot-reloads on code changes

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest -v

# Run specific test file
pytest backend/tests/test_health.py -v

# Run with coverage
pytest --cov=backend/app --cov-report=html
```

### Database Management

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Git Operations

Firebase Studio includes GitLens and Git Graph extensions:

1. Use the Source Control panel (Ctrl+Shift+G)
2. View git history with Git Graph
3. Compare changes with GitLens
4. Commit and push directly from the IDE

## IDE Extensions Included

### Python Development
- Python Language Server (Pylance)
- Debugger (debugpy)
- Black Formatter
- isort Import Sorter
- Flake8 Linter

### JavaScript/TypeScript/React
- ESLint
- Prettier Formatter
- React Snippets
- Tailwind CSS IntelliSense
- Styled Components

### Database Tools
- SQLTools
- PostgreSQL Driver
- SQLite Driver

### Cloud & Firebase
- Google Cloud Code
- Firebase Tools

### Productivity
- GitLens
- Git Graph
- REST Client
- TODO Highlight
- Better Comments

## Advanced Configuration

### Customizing the Environment

Edit `.idx/dev.nix` to:

1. Add more packages: Add to the `packages` list
2. Change environment variables: Modify the `env` section
3. Add more IDE extensions: Add to `idx.extensions`
4. Modify preview commands: Edit `idx.previews`

After editing, Firebase Studio will automatically reload the configuration.

### Adding Services

To add more services (like Redis):

```nix
services = {
  redis = {
    enable = true;
    port = 6379;
  };
};
```

## Optimization Tips

1. **Build Cache**: Firebase Studio caches Nix builds for faster restarts
2. **Incremental Builds**: Only changed dependencies are reinstalled
3. **Preview Optimization**: Use `--reload` for development, remove for production
4. **Resource Management**: Monitor resource usage with `htop` (included)

## Troubleshooting

### Environment Not Loading

1. Check the Nix build logs in the terminal
2. Verify `.idx/dev.nix` syntax is correct
3. Try reloading the workspace

### Python Dependencies Not Installing

```bash
# Manually recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Node Dependencies Issues

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Connection Issues

```bash
# Check PostgreSQL service status
pg_isready

# Restart PostgreSQL service
# Firebase Studio will handle this automatically
```

## Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use Firebase Secret Manager** for production secrets
3. **Rotate API keys regularly**
4. **Use environment-specific configurations**
5. **Enable Firebase App Check** for production deployments

## Deployment

### Deploying to Firebase

```bash
# Build frontend
cd frontend
npm run build

# Deploy with Firebase
firebase deploy
```

### Deploying to Google Cloud Run

```bash
# Build backend container
docker build -t seatsync-backend ./backend

# Deploy to Cloud Run
gcloud run deploy seatsync-backend \
  --source . \
  --platform managed \
  --region us-central1
```

## Additional Resources

- [Firebase Studio Documentation](https://firebase.google.com/docs/studio)
- [dev.nix Reference](https://firebase.google.com/docs/studio/devnix-reference)
- [Nix Package Search](https://search.nixos.org/packages)
- [SeatSync API Documentation](./API_INTEGRATION_GUIDE.md)
- [SeatSync Implementation Guide](./IMPLEMENTATION_GUIDE.md)

## Support

For issues specific to:
- **Firebase Studio**: [Firebase Support](https://firebase.google.com/support)
- **SeatSync Application**: [GitHub Issues](https://github.com/elliotttmiller/SeatSync/issues)
- **Nix Configuration**: [NixOS Discourse](https://discourse.nixos.org/)

## License

This configuration is part of the SeatSync project and follows the same MIT license.

---

**Last Updated**: October 2024
**Firebase Studio Version**: Latest (using stable-24.05 channel)
