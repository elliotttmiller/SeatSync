# Firebase Studio Quick Reference Card

Quick reference for common Firebase Studio operations with SeatSync.

## 🚀 Getting Started

```bash
# Open in Firebase Studio
https://idx.google.com/

# Import Repository
elliotttmiller/SeatSync

# Wait for setup (~10 minutes)
# All dependencies install automatically
```

## 📋 Common Commands

### Python/Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Run backend server
cd backend && uvicorn app.main:app --reload

# Run tests
pytest -v

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "message"

# Linting
black backend/app
flake8 backend/app
```

### Node.js/Frontend
```bash
# Install dependencies
cd frontend && npm install

# Start dev server
npm start

# Run tests
npm test

# Build for production
npm run build

# Linting
npm run lint
npm run lint:fix
```

### Streamlit Dashboard
```bash
# Run dashboard
streamlit run streamlit_app.py
```

## 🔧 VS Code Tasks (Ctrl+Shift+P → "Run Task")

- **Setup: Install All Dependencies**
- **Backend: Start Server**
- **Frontend: Start Dev Server**
- **Streamlit: Start Dashboard**
- **Test: Run All Tests**
- **DB: Run Migrations**
- **Lint: Python/Frontend**
- **Format: Python/Frontend**
- **Firebase: Deploy**
- **Docker: Build/Run**

## 🐛 Debugging (F5)

- **Python: FastAPI Backend** - Debug backend with breakpoints
- **Python: Current File** - Debug current Python file
- **Python: Pytest** - Debug tests
- **React: Frontend** - Debug frontend
- **Full Stack** - Debug both backend and frontend

## 🌐 Preview URLs

- **Backend API**: `https://8000-[workspace].idx.dev`
- **Frontend**: `https://3000-[workspace].idx.dev`
- **Streamlit**: `https://8501-[workspace].idx.dev`

Click port numbers in terminal or use "Ports" panel.

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Command Palette | `Ctrl+Shift+P` |
| Quick Open File | `Ctrl+P` |
| New Terminal | ``Ctrl+` `` |
| Toggle Sidebar | `Ctrl+B` |
| Search Files | `Ctrl+Shift+F` |
| Start Debugging | `F5` |
| Git Panel | `Ctrl+Shift+G` |
| Run Task | `Ctrl+Shift+B` |
| Problems Panel | `Ctrl+Shift+M` |
| Extensions | `Ctrl+Shift+X` |

## 📁 File Structure

```
.
├── .idx/                    # Firebase Studio config
│   ├── dev.nix             # Main configuration
│   └── validate-config.sh  # Validation script
├── backend/                # Python FastAPI backend
│   ├── app/               # Application code
│   ├── tests/             # Test files
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── src/               # React components
│   └── package.json       # Node dependencies
├── .vscode/               # VS Code config
├── .firebaserc            # Firebase project
├── firebase.json          # Firebase hosting/functions
├── firestore.rules        # Database security
└── storage.rules          # Storage security
```

## 🔥 Firebase Commands

```bash
# Login
firebase login

# Initialize (already done)
firebase init

# Deploy all
firebase deploy

# Deploy specific service
firebase deploy --only hosting:frontend
firebase deploy --only functions
firebase deploy --only firestore:rules

# Test locally
firebase emulators:start

# View logs
firebase logs:all
```

## ☁️ Google Cloud Commands

```bash
# Deploy backend to Cloud Run
gcloud run deploy seatsync-backend \
  --source ./backend \
  --platform managed \
  --region us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision"

# Connect to Cloud SQL
gcloud sql connect seatsync-db --user=seatsync
```

## 📊 Database Operations

### SQLite (Development)
```bash
# Open database
sqlite3 seatsync.db

# Common queries
.tables
.schema tablename
SELECT * FROM users LIMIT 10;
```

### PostgreSQL (Production)
```bash
# Connect via Cloud SQL Proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# Connect with psql
psql -h localhost -U seatsync -d seatsync_prod
```

## 🧪 Testing

```bash
# All tests
pytest -v

# Specific file
pytest backend/tests/test_health.py -v

# With coverage
pytest --cov=backend/app --cov-report=html

# Watch mode
pytest-watch
```

## 📦 Package Management

### Python
```bash
# Add package
pip install package-name
pip freeze > backend/requirements.txt

# Remove package
pip uninstall package-name
```

### Node.js
```bash
# Add package
npm install package-name

# Add dev dependency
npm install --save-dev package-name

# Remove package
npm uninstall package-name
```

## 🔐 Environment Variables

```bash
# Development (.env)
SECRET_KEY=dev-secret
DATABASE_URL=sqlite:///./seatsync.db

# Production (Secret Manager)
gcloud secrets create SECRET_KEY --data-file=-
gcloud secrets versions access latest --secret="SECRET_KEY"
```

## 🎨 Code Formatting

```bash
# Python (Black)
black backend/app
black --check backend/app

# JavaScript/TypeScript (Prettier)
cd frontend
npm run lint:fix

# Auto-format on save (enabled in VS Code)
```

## 🔍 Code Quality

```bash
# Python linting
flake8 backend/app
mypy backend/app

# JavaScript linting
cd frontend
npm run lint

# Type checking
npm run type-check
```

## 📝 Git Operations

```bash
# Stage changes
git add .

# Commit
git commit -m "message"

# Push
git push

# Pull
git pull

# New branch
git checkout -b feature-name

# View history (use Git Graph extension)
```

## 🛠️ Troubleshooting

### Clear caches and restart
```bash
# Python
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Node.js
cd frontend
rm -rf node_modules package-lock.json
npm install

# Database
rm seatsync.db
alembic upgrade head
```

### Check logs
```bash
# Backend logs - in "Backend" terminal tab
# Frontend logs - in "Frontend" terminal tab
# System logs - View → Output → Select log type
```

### Kill processes
```bash
# Kill by port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Kill by name
pkill -f uvicorn
pkill -f "npm start"
```

## 💡 Pro Tips

1. **Split Terminal**: Right-click terminal → Split terminal
2. **Multiple Previews**: Click port numbers to open multiple previews
3. **REST Client**: Create `.http` files to test APIs without Postman
4. **GitLens**: Hover over code to see git blame
5. **TODO Tree**: View all TODOs/FIXMEs in sidebar
6. **Peek Definition**: Alt+F12 on any symbol
7. **Multi-cursor**: Alt+Click or Ctrl+Alt+↓/↑
8. **Command Palette**: Your best friend (Ctrl+Shift+P)

## 📚 Documentation

- **Setup Guide**: `FIREBASE_STUDIO_SETUP.md`
- **Quick Start**: `FIREBASE_STUDIO_QUICK_START.md`
- **Deployment**: `FIREBASE_DEPLOYMENT_GUIDE.md`
- **API Guide**: `API_INTEGRATION_GUIDE.md`
- **.idx Config**: `.idx/README.md`

## 🆘 Get Help

- **Firebase Studio**: [firebase.google.com/docs/studio](https://firebase.google.com/docs/studio)
- **SeatSync Issues**: [github.com/elliotttmiller/SeatSync/issues](https://github.com/elliotttmiller/SeatSync/issues)
- **Stack Overflow**: Tag `firebase-studio` or `google-cloud-platform`

---

**Keep this handy!** Bookmark this file for quick reference.
