# =============================================================================
# Bio MCP Research Agent — Dockerfile
# =============================================================================
# Multi-stage build:
#   Stage 1 (builder): Install Python deps + Node.js
#   Stage 2 (runtime): Copy built app, run
# =============================================================================

# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install Node.js (required for @modelcontextprotocol/server-filesystem via npx)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# ── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.source="https://github.com/mdbasit897/bio-mcp-research-agent"
LABEL org.opencontainers.image.description="Bio MCP Research Agent"

# Install Node.js (required for MCP filesystem server)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# Create output directory
RUN mkdir -p /app/research_outputs && chown -R appuser:appuser /app

USER appuser

# Default: run the agent with the example prompt
ENTRYPOINT ["python", "src/agent_cli.py", "--example"]
CMD []

# ── Usage ────────────────────────────────────────────────────────────────────
# Build:   docker build -t bio-mcp-research-agent .
# Run:     docker run --env-file .env bio-mcp-research-agent
# Custom:  docker run --env-file .env bio-mcp-research-agent --prompt "Your research prompt"
# Shell:   docker run --env-file .env -it --entrypoint /bin/bash bio-mcp-research-agent
