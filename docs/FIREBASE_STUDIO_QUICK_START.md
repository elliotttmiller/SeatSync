# Firebase Studio Quick Start Guide

Get SeatSync running in Firebase Studio in under 5 minutes!

## What is Firebase Studio?

Firebase Studio (formerly Project IDX) is Google's cloud-based development environment that provides:
- ✅ Pre-configured development environment
- ✅ No local setup required
- ✅ Automatic dependency management
- ✅ Integrated preview servers
- ✅ Built-in VS Code with extensions
- ✅ Cloud-powered compute resources

## Quick Start (3 Steps)

### Step 1: Open in Firebase Studio

1. Go to [idx.google.com](https://idx.google.com/)
2. Sign in with your Google account
3. Click "Import from GitHub"
4. Enter: `elliotttmiller/SeatSync`
5. Click "Import"

### Step 2: Wait for Automatic Setup (5-10 minutes)

Firebase Studio will automatically:
- ✅ Install all system packages (Python, Node.js, databases, etc.)
- ✅ Create Python virtual environment
- ✅ Install Python dependencies (~200 packages)
- ✅ Run database migrations
- ✅ Install browser automation tools

Watch the terminal for progress. When you see "✓ Workspace ready", you're good to go!

### Step 3: Start Developing

**Streamlit Dashboard** (Primary Development Interface) is automatically running at:
- URL: Click the "Web Preview" button → Port 8501
- Or: `https://8501-[your-workspace-url]`
- **This is your main interface for testing and development**

**Backend API Server** is automatically running at:
- URL: Click the "Web Preview" button → Port 8000
- Or: `https://8000-[your-workspace-url]`
- **Production-grade API with all integrations**

## What's Included?

### Pre-installed Packages
- **Python 3.11** with 200+ ML/AI libraries
- **PostgreSQL 15** database
- **Streamlit** for interactive development
- **Firebase Tools** for deployment
- **Google Cloud SDK** for cloud integration
- **Git & GitHub CLI** for version control

### Pre-configured IDE Extensions
- Python (Pylance, Black, Flake8)
- Database tools (SQLTools)
- Git tools (GitLens, Git Graph)
- Firebase & Google Cloud tools
- And 25+ more productivity extensions!

### Pre-configured Services
- PostgreSQL database (auto-starts)
- Streamlit dashboard (primary interface)
- Backend API (production logic)
- Redis cache (optional)
- Multi-service preview (backend and Streamlit)

## Common Tasks

### View Logs
```bash
# Backend logs - visible in the "Backend" terminal tab
# Streamlit logs - visible in the "Streamlit" terminal tab
```

### Run Tests
```bash
# Open new terminal (Ctrl+`)
source .venv/bin/activate
pytest -v
```

### Access Database
```bash
# Use SQLTools extension (left sidebar)
# Or command line:
sqlite3 seatsync.db
# Or PostgreSQL:
psql -h localhost -U seatsync -d seatsync
```

### Make Code Changes
- Edit any file - changes auto-reload!
- Backend: FastAPI auto-reloads
- Streamlit: Auto-reloads on file save
- Instant feedback in preview windows

### Commit Changes
- Use Source Control panel (Ctrl+Shift+G)
- Or Git terminal commands
- GitLens shows inline blame and history

### Deploy to Production
```bash
# Deploy backend to Cloud Run

# Backend to Cloud Run
gcloud run deploy seatsync-backend --source ./backend
```

## Environment Variables

Create `.env` file in root directory:

```bash
# Copy template
cp backend/.env.test .env

# Edit with your keys (optional for development)
# Most features work without API keys!
```

## Keyboard Shortcuts

- `Ctrl+` ` - New terminal
- `Ctrl+Shift+P` - Command palette
- `Ctrl+P` - Quick file open
- `Ctrl+Shift+F` - Search across files
- `Ctrl+B` - Toggle sidebar
- `F5` - Start debugging
- `Ctrl+Shift+D` - Debug panel

## Pro Tips

### 1. Multiple Terminals
Use split terminals to monitor all services:
- Terminal 1: Backend logs
- Terminal 2: Frontend logs
- Terminal 3: Commands/tests

### 2. Extension Power
- **GitLens**: Hover over any line to see git blame
- **Better Comments**: Use `// TODO:`, `// FIXME:` for highlights
- **REST Client**: Create `.http` files to test APIs
- **SQLTools**: Browse database without leaving IDE

### 3. Debugging
- Set breakpoints in Python code
- Press F5 → Select "Python: FastAPI Backend"
- Interactive debugging in the IDE!

### 4. Task Runner
- `Ctrl+Shift+P` → "Run Task"
- Pre-configured tasks:
  - Start Backend
  - Start Frontend
  - Run Tests
  - Database Migrations
  - Linting
  - Formatting

### 5. Preview Management
- Click port number in terminal to open preview
- Use "Ports" panel to manage all previews
- Each service has its own preview URL

## Troubleshooting

### "Dependencies not installed"
```bash
# Manually reinstall
source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

### "Database connection failed"
```bash
# Reset database
rm seatsync.db
alembic upgrade head
```

### "Port already in use"
```bash
# Kill process on port
lsof -ti:8000 | xargs kill -9
# Or restart the workspace
```

### "Python module not found"
```bash
# Verify virtual environment
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

## Performance Tips

1. **Close unused previews** - Saves resources
2. **Use split terminals** - Better than opening new ones
3. **Collapse file tree** - Faster file operations
4. **Disable auto-save** - If editing large files
5. **Use search shortcuts** - Faster than file tree navigation

## What's Different from Local Dev?

### Advantages ✅
- No local setup needed
- Cloud-powered resources
- Consistent environment
- Easy sharing/collaboration
- Integrated with Firebase/GCP
- No "works on my machine" issues

### Limitations ⚠️
- Requires internet connection
- Workspace may sleep after inactivity
- Some extensions may not work
- Limited to cloud resources

## Next Steps

1. **Explore the Code**: Use `Ctrl+P` to jump to files
2. **Read Documentation**: Check other `.md` files in root
3. **Run Tests**: `pytest -v` to see everything works
4. **Try API**: Use REST Client extension or browser
5. **Make Changes**: Edit and see instant results!

## Learn More

- **Full Setup Guide**: See `FIREBASE_STUDIO_SETUP.md`
- **Deployment Guide**: See `FIREBASE_DEPLOYMENT_GUIDE.md`
- **API Documentation**: See `API_INTEGRATION_GUIDE.md`
- **Implementation Guide**: See `IMPLEMENTATION_GUIDE.md`

## Get Help

- **Firebase Studio Docs**: [firebase.google.com/docs/studio](https://firebase.google.com/docs/studio)
- **SeatSync Issues**: [github.com/elliotttmiller/SeatSync/issues](https://github.com/elliotttmiller/SeatSync/issues)
- **Community**: Join discussions in GitHub

---

**Happy Coding! 🚀**

Built with ❤️ for developers by the SeatSync team.
