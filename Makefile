.PHONY: help install setup dev start frontend chat chat-dev kill-port-3000 clean clean-output clean-branches test lint format

# Default target
help:
	@echo "Time Analysis Tool - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install dependencies using uv"
	@echo "  make setup            - Full project setup with uv (create venv + install)"
	@echo "  make dev              - Setup development environment"
	@echo ""
	@echo "Running the Application:"
	@echo "  make start            - Start the Streamlit web UI (hot reload enabled)"
	@echo "  make chat             - Start on port 3000 (kills existing process first)"
	@echo "  make chat-dev         - Start on port 3000 with fresh cache"
	@echo "  make frontend         - Alias for 'make start'"
	@echo "  make kill-port-3000   - Kill any process running on port 3000"
	@echo ""
	@echo "Git & Branch Management:"
	@echo "  make clean-branches   - Remove local branches that no longer exist on remote"
	@echo "  make fetch            - Fetch latest changes from remote"
	@echo "  make status           - Show git status"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Clean all output and cache files"
	@echo "  make clean-output     - Clean analysis output directories"
	@echo "  make clean-cache      - Clean Python cache files"
	@echo ""
	@echo "Analysis (CLI):"
	@echo "  make analyze          - Run CLI analysis on example data"
	@echo "  make summary          - Generate summary of example data"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code"
	@echo ""

# ============================================
# Setup & Installation
# ============================================

install:
	@echo "📦 Installing dependencies with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"

setup:
	@echo "🚀 Setting up project with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@echo "Creating virtual environment..."
	uv venv
	@echo "Installing dependencies..."
	uv pip install -r requirements.txt
	@echo "✅ Setup complete!"
	@echo ""
	@echo "To activate the virtual environment:"
	@echo "  source .venv/bin/activate  (Linux/Mac)"
	@echo "  .venv\\Scripts\\activate     (Windows)"

dev: setup
	@echo "🔧 Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo "✅ .env file created. Please add your API keys."; \
	else \
		echo "✅ .env file already exists."; \
	fi
	@mkdir -p data
	@echo "✅ Development environment ready!"

# ============================================
# Running the Application
# ============================================

start: frontend

frontend:
	@echo "🌐 Starting Streamlit web UI..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv run streamlit run app.py

kill-port-3000:
	@echo "🔪 Checking for processes on port 3000..."
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   No process found on port 3000"

chat: kill-port-3000
	@echo "💬 Starting Streamlit on port 3000 with hot reload..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv run streamlit run app.py --server.port 3000

chat-dev: kill-port-3000
	@echo "🔥 Starting Streamlit on port 3000 with fresh cache..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@echo "Clearing Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Starting Streamlit..."
	uv run streamlit run app.py --server.port 3000

# ============================================
# Git & Branch Management
# ============================================

fetch:
	@echo "📡 Fetching latest changes from remote..."
	git fetch origin --prune
	@echo "✅ Fetch complete!"

clean-branches: fetch
	@echo "🧹 Cleaning up local branches that no longer exist on remote..."
	@echo ""
	@echo "Branches to be deleted:"
	@git branch -vv | grep ': gone]' | awk '{print $$1}' || echo "  (none)"
	@echo ""
	@read -p "Continue with deletion? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		git branch -vv | grep ': gone]' | awk '{print $$1}' | xargs -r git branch -D; \
		echo "✅ Cleanup complete!"; \
	else \
		echo "❌ Cleanup cancelled."; \
	fi

status:
	@echo "📊 Git Status"
	@echo "============="
	@git status
	@echo ""
	@echo "📋 Branches"
	@echo "==========="
	@git branch -vv

# ============================================
# Cleanup
# ============================================

clean: clean-output clean-cache
	@echo "✨ All cleanup complete!"

clean-output:
	@echo "🧹 Cleaning output directories..."
	rm -rf time_analysis_output/
	rm -rf output/
	@echo "✅ Output directories cleaned!"

clean-cache:
	@echo "🧹 Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache files cleaned!"

# ============================================
# Analysis (CLI)
# ============================================

analyze:
	@echo "📊 Running analysis on example data..."
	python analyze.py analyze "example data/" --output output/
	@echo "✅ Analysis complete! Check output/ directory."

summary:
	@echo "📊 Generating summary of example data..."
	python analyze.py summary "example data/" --output output/
	@echo "✅ Summary complete! Check output/ directory."

# ============================================
# Development Tools
# ============================================

lint:
	@echo "🔍 Running linting checks..."
	@command -v ruff >/dev/null 2>&1 && ruff check . || echo "⚠️  ruff not installed. Run: uv pip install ruff"
	@echo "✅ Linting complete!"

format:
	@echo "✨ Formatting code..."
	@command -v ruff >/dev/null 2>&1 && ruff format . || echo "⚠️  ruff not installed. Run: uv pip install ruff"
	@echo "✅ Formatting complete!"

# ============================================
# Additional Helpful Targets
# ============================================

.PHONY: check-deps update-deps

check-deps:
	@echo "🔍 Checking dependencies..."
	@command -v uv >/dev/null 2>&1 && echo "✅ uv installed" || echo "❌ uv not installed"
	@command -v python3 >/dev/null 2>&1 && echo "✅ python3 installed" || echo "❌ python3 not installed"
	@command -v git >/dev/null 2>&1 && echo "✅ git installed" || echo "❌ git not installed"

update-deps:
	@echo "⬆️  Updating dependencies..."
	uv pip install --upgrade -r requirements.txt
	@echo "✅ Dependencies updated!"
