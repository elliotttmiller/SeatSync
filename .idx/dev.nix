# Firebase Studio Development Environment Configuration
# Complete and professionally optimized for SeatSync project
# Reference: https://firebase.google.com/docs/studio/devnix-reference

{ pkgs, ... }: {
  # Use stable Nix channel for reliability
  channel = "stable-24.05";

  # Comprehensive package list for full-stack development
  packages = [
    # Python Development (Backend)
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.python311Packages.setuptools
    
    # Node.js Development (Frontend)
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.nodePackages.yarn
    pkgs.nodePackages.pnpm
    
    # Database Tools
    pkgs.postgresql_15
    pkgs.sqlite
    pkgs.redis
    
    # Firebase Tools
    pkgs.firebase-tools
    
    # Google Cloud SDK
    pkgs.google-cloud-sdk
    
    # Development Tools
    pkgs.git
    pkgs.gh
    pkgs.curl
    pkgs.wget
    pkgs.jq
    pkgs.htop
    pkgs.tree
    
    # Build Tools
    pkgs.gcc
    pkgs.gnumake
    pkgs.cmake
    pkgs.pkg-config
    
    # Python C Extensions Dependencies (for ML libraries)
    pkgs.openssl
    pkgs.zlib
    pkgs.libffi
    pkgs.bzip2
    pkgs.readline
    pkgs.ncurses
    pkgs.gdbm
    pkgs.xz
    
    # Additional utilities
    pkgs.unzip
    pkgs.zip
    pkgs.which
    pkgs.watchman
  ];

  # Environment Variables Configuration
  env = {
    # Python Configuration
    PYTHONUNBUFFERED = "1";
    PIP_NO_CACHE_DIR = "1";
    PYTHON_VERSION = "3.11";
    
    # Node Configuration
    NODE_ENV = "development";
    NODE_OPTIONS = "--max-old-space-size=4096";
    
    # Database Configuration
    DATABASE_URL = "sqlite+aiosqlite:///./seatsync.db";
    POSTGRES_HOST = "localhost";
    POSTGRES_PORT = "5432";
    POSTGRES_DB = "seatsync";
    POSTGRES_USER = "seatsync";
    
    # Application Settings
    SECRET_KEY = "dev-secret-key-change-in-production";
    JWT_SECRET_KEY = "dev-jwt-secret-key-change-in-production";
    CORS_ORIGIN = "http://localhost:3000";
    
    # API Configuration Placeholders
    GOOGLE_PROJECT_ID = "seatsync-project";
    FIREBASE_PROJECT_ID = "seatsync-project";
    
    # Development Mode
    DEBUG = "true";
    LOG_LEVEL = "info";
    
    # Path Configuration
    PATH = "/home/user/.local/bin:$PATH";
  };

  # IDX Extensions - Comprehensive tooling for development
  idx = {
    # VS Code Extensions
    extensions = [
      # Python Development
      "ms-python.python"
      "ms-python.vscode-pylance"
      "ms-python.debugpy"
      "ms-python.black-formatter"
      "ms-python.isort"
      "ms-python.flake8"
      
      # JavaScript/TypeScript/React Development
      "dbaeumer.vscode-eslint"
      "esbenp.prettier-vscode"
      "dsznajder.es7-react-js-snippets"
      "bradlc.vscode-tailwindcss"
      "styled-components.vscode-styled-components"
      
      # Git & Version Control
      "eamodio.gitlens"
      "mhutchie.git-graph"
      
      # Database Tools
      "mtxr.sqltools"
      "mtxr.sqltools-driver-pg"
      "mtxr.sqltools-driver-sqlite"
      
      # Firebase & Google Cloud
      "GoogleCloudTools.cloudcode"
      "toba.vsfire"
      
      # Docker & DevOps
      "ms-azuretools.vscode-docker"
      "ms-kubernetes-tools.vscode-kubernetes-tools"
      
      # API Development
      "humao.rest-client"
      "Postman.postman-for-vscode"
      
      # Code Quality & Formatting
      "EditorConfig.EditorConfig"
      "aaron-bond.better-comments"
      "streetsidesoftware.code-spell-checker"
      
      # Productivity
      "vscode-icons-team.vscode-icons"
      "PKief.material-icon-theme"
      "wayou.vscode-todo-highlight"
      "Gruntfuggly.todo-tree"
      
      # AI & ML Development
      "ms-toolsai.jupyter"
      "ms-toolsai.vscode-jupyter-cell-tags"
      "ms-toolsai.vscode-jupyter-slideshow"
      
      # Testing
      "hbenl.vscode-test-explorer"
      "LittleFoxTeam.vscode-python-test-adapter"
      
      # Markdown & Documentation
      "yzhang.markdown-all-in-one"
      "DavidAnson.vscode-markdownlint"
    ];

    # Workspace Configuration
    workspace = {
      # Auto-create virtual environment for Python
      onCreate = {
        # Setup Python virtual environment
        setup-python-env = ''
          python3 -m venv .venv
          source .venv/bin/activate
          pip install --upgrade pip
          pip install -r backend/requirements.txt
        '';
        
        # Initialize database
        setup-database = ''
          alembic upgrade head
        '';
        
        # Install scrapling browsers
        setup-scrapling = ''
          source .venv/bin/activate
          scrapling install
        '';
      };
      
      # Run on workspace start
      onStart = {
        # Start PostgreSQL if needed
        start-postgres = ''
          # PostgreSQL will be started by the service
          echo "PostgreSQL service configured"
        '';
      };
    };

    # Preview Configuration - Streamlit-focused development
    previews = {
      enable = true;
      previews = {
        # Backend API Server
        backend = {
          command = [
            "sh"
            "-c"
            "source .venv/bin/activate && cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
          ];
          manager = "web";
          env = {
            PORT = "8000";
            PYTHONUNBUFFERED = "1";
          };
        };
        
        # Streamlit Dashboard (Primary Development Interface)
        streamlit = {
          command = [
            "sh"
            "-c"
            "source .venv/bin/activate && streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"
          ];
          manager = "web";
          env = {
            PORT = "8501";
          };
        };
      };
    };
  };

  # Services Configuration
  services = {
    # PostgreSQL Database Service
    postgres = {
      enable = true;
      package = pkgs.postgresql_15;
      extensions = extensions: [
        extensions.postgis
      ];
    };
    
    # Redis Cache Service (Optional)
    redis = {
      enable = false;
      port = 6379;
    };
  };
}
