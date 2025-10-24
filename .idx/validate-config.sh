#!/bin/bash
# Firebase Studio Configuration Validator
# Validates that all required components are properly configured

set -e

echo "🔍 Validating Firebase Studio Configuration..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        return 1
    fi
}

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Command available: $1 ($(command -v $1))"
        return 0
    else
        echo -e "${RED}✗${NC} Command not found: $1"
        return 1
    fi
}

# Track validation status
FAILED=0

# Check configuration files
echo "📁 Checking Configuration Files..."
check_file ".idx/dev.nix" || FAILED=1
check_file ".firebaserc" || FAILED=1
check_file "firebase.json" || FAILED=1
check_file "firestore.rules" || FAILED=1
check_file "storage.rules" || FAILED=1
check_file ".editorconfig" || FAILED=1
check_file ".vscode/settings.json" || FAILED=1
check_file ".vscode/launch.json" || FAILED=1
check_file ".vscode/tasks.json" || FAILED=1
echo ""

# Check documentation
echo "📚 Checking Documentation..."
check_file "FIREBASE_STUDIO_SETUP.md" || FAILED=1
check_file "FIREBASE_STUDIO_QUICK_START.md" || FAILED=1
check_file "FIREBASE_DEPLOYMENT_GUIDE.md" || FAILED=1
echo ""

# Check required commands
echo "🛠️  Checking Required Tools..."
check_command "python3" || FAILED=1
check_command "node" || FAILED=1
check_command "npm" || FAILED=1
check_command "git" || FAILED=1
check_command "firebase" || echo -e "${YELLOW}⚠${NC} Firebase CLI not yet available (will be installed)"
check_command "gcloud" || echo -e "${YELLOW}⚠${NC} Google Cloud SDK not yet available (will be installed)"
echo ""

# Check Python version
echo "🐍 Checking Python Version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION (>= 3.11 required)"
else
    echo -e "${RED}✗${NC} Python version: $PYTHON_VERSION (3.11+ required)"
    FAILED=1
fi
echo ""

# Check Node version
echo "📦 Checking Node.js Version..."
NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

if [ "$NODE_MAJOR" -ge 18 ]; then
    echo -e "${GREEN}✓${NC} Node.js version: v$NODE_VERSION (>= 18 required)"
else
    echo -e "${RED}✗${NC} Node.js version: v$NODE_VERSION (18+ required)"
    FAILED=1
fi
echo ""

# Check project structure
echo "📂 Checking Project Structure..."
check_file "backend/requirements.txt" || FAILED=1
check_file "backend/app/main.py" || FAILED=1
check_file "frontend/package.json" || FAILED=1
check_file "pyproject.toml" || FAILED=1
check_file "alembic.ini" || FAILED=1
echo ""

# Check virtual environment
echo "🔧 Checking Virtual Environment..."
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    if [ -f ".venv/bin/activate" ]; then
        echo -e "${GREEN}✓${NC} Virtual environment is valid"
    else
        echo -e "${RED}✗${NC} Virtual environment is corrupted"
        FAILED=1
    fi
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not created yet (will be created on workspace start)"
fi
echo ""

# Check frontend dependencies
echo "⚛️  Checking Frontend Setup..."
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed yet (will be installed on workspace start)"
fi
echo ""

# Validate dev.nix syntax (basic check)
echo "🔍 Validating dev.nix Syntax..."
if grep -q "{ pkgs, ... }: {" ".idx/dev.nix" && \
   grep -q "channel = " ".idx/dev.nix" && \
   grep -q "packages = " ".idx/dev.nix"; then
    echo -e "${GREEN}✓${NC} dev.nix syntax looks valid"
else
    echo -e "${RED}✗${NC} dev.nix syntax may be invalid"
    FAILED=1
fi
echo ""

# Check Firebase configuration
echo "🔥 Validating Firebase Configuration..."
if grep -q "seatsync-project" ".firebaserc"; then
    echo -e "${YELLOW}⚠${NC} Using default Firebase project ID 'seatsync-project'"
    echo -e "  ${YELLOW}→${NC} Remember to update .firebaserc with your actual project ID"
else
    echo -e "${GREEN}✓${NC} Firebase project ID configured"
fi
echo ""

# Final summary
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Configuration validation passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Open this project in Firebase Studio (idx.google.com)"
    echo "2. Wait for automatic setup to complete"
    echo "3. Update .env with your API keys"
    echo "4. Update .firebaserc with your Firebase project ID"
    echo "5. Start developing!"
    exit 0
else
    echo -e "${RED}❌ Configuration validation failed!${NC}"
    echo ""
    echo "Please review the errors above and fix them."
    echo "See FIREBASE_STUDIO_SETUP.md for detailed instructions."
    exit 1
fi
