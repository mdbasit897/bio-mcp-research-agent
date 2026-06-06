# =============================================================================
# Bio MCP Research Agent — Makefile
# =============================================================================
# Usage: make <target>
# =============================================================================

.PHONY: install test lint typecheck coverage clean docker-build docker-run preflight help

# ── Defaults ─────────────────────────────────────────────────────────────────
VENV     := venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
ACTIVATE := . $(VENV)/bin/activate

# ── Installation ─────────────────────────────────────────────────────────────
install: $(VENV)/.installed
	@echo "✅ Dependencies installed."

$(VENV)/.installed: requirements.txt pyproject.toml
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"
	touch $(VENV)/.installed

# ── Quick Check ──────────────────────────────────────────────────────────────
preflight:
	@echo "🔍 Running preflight checks..."
	@command -v python3 || { echo "❌ python3 not found. Install Python 3.10+."; exit 1; }
	@python3 -c "import sys; assert sys.version_info >= (3,10), f'Python 3.10+ required, got {sys.version_info[:2]}'" && echo "✅ Python version OK" || { echo "❌ Python version too old."; exit 1; }
	@command -v node || { echo "⚠️  Node.js not found. MCP filesystem server requires Node.js ≥18."; }
	@command -v npm || { echo "⚠️  npm not found."; }
	@[ -f .env ] || { echo "⚠️  .env not found. Run: cp .env.example .env"; }
	@echo "✅ Preflight complete."

# ── Testing ──────────────────────────────────────────────────────────────────
test: $(VENV)/.installed
	$(ACTIVATE) && pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=85

test-unit: $(VENV)/.installed
	$(ACTIVATE) && pytest tests/unit/ -v --cov=src --cov-report=term-missing

test-integration: $(VENV)/.installed
	$(ACTIVATE) && pytest tests/integration/ -v --cov=src --cov-report=term-missing --cov-fail-under=5

test-e2e: $(VENV)/.installed
	$(ACTIVATE) && pytest tests/e2e/ -v --cov=src --cov-report=term-missing -m "not real_api" --cov-fail-under=5

# ── Code Quality ─────────────────────────────────────────────────────────────
lint: $(VENV)/.installed
	$(ACTIVATE) && flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	$(ACTIVATE) && flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

typecheck: $(VENV)/.installed
	$(ACTIVATE) && mypy src/

security: $(VENV)/.installed
	$(ACTIVATE) && bandit -r src/ -f json -o bandit-report.json
	$(ACTIVATE) && safety check

# ── Coverage ─────────────────────────────────────────────────────────────────
coverage: $(VENV)/.installed
	$(ACTIVATE) && pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml --cov-fail-under=85
	@echo "📊 HTML report: htmlcov/index.html"

# ── Cleanup ──────────────────────────────────────────────────────────────────
clean:
	rm -rf $(VENV) .pytest_cache .coverage htmlcov coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	@echo "🧹 Cleaned."

# ── Docker ───────────────────────────────────────────────────────────────────
docker-build:
	docker build -t bio-mcp-research-agent .

docker-run: docker-build
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/research_outputs:/app/research_outputs \
		bio-mcp-research-agent

docker-shell: docker-build
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/research_outputs:/app/research_outputs \
		bio-mcp-research-agent /bin/bash

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "Bio MCP Research Agent — Makefile targets:"
	@echo ""
	@echo "  install       Set up virtual environment and install dependencies"
	@echo "  preflight     Check Python, Node.js, and .env"
	@echo "  test          Run all tests with coverage"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  test-e2e      Run E2E tests (mocked only)"
	@echo "  lint          Run flake8 linting"
	@echo "  typecheck     Run mypy type checking"
	@echo "  security      Run bandit + safety checks"
	@echo "  coverage      Run tests and generate HTML coverage report"
	@echo "  clean         Remove build artifacts and venv"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Build and run the agent in Docker"
	@echo "  docker-shell  Build and open a shell in the Docker container"
	@echo "  help          Show this help message"
