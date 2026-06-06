#!/usr/bin/env python3
"""
Preflight check for Bio MCP Research Agent.

Verifies that the environment meets all prerequisites before running the agent.
Run this after cloning to catch issues early.

Usage:
    python scripts/preflight.py
    python scripts/preflight.py --check-env   # Also verify .env has required keys
"""

import sys
import os
import subprocess
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(condition: bool, pass_msg: str, fail_msg: str) -> bool:
    """Print a pass/fail result and return success status."""
    if condition:
        print(f"  {GREEN}✅{RESET} {pass_msg}")
        return True
    else:
        print(f"  {RED}❌{RESET} {fail_msg}")
        return False


def warn(msg: str):
    print(f"  {YELLOW}⚠️ {msg}{RESET}")


def main():
    print(f"\n{BOLD}🔍 Bio MCP Research Agent — Preflight Check{RESET}\n")

    all_ok = True
    root = Path(__file__).resolve().parent.parent

    # ── 1. Python version ───────────────────────────────────────────────────
    print(f"{BOLD}Python{RESET}")
    py_version = sys.version_info
    py_ok = check(
        py_version >= (3, 10),
        f"Python {py_version.major}.{py_version.minor}.{py_version.micro} (≥3.10 required)",
        f"Python {py_version.major}.{py_version.minor} — need 3.10+",
    )
    all_ok = all_ok and py_ok
    print()

    # ── 2. Node.js ──────────────────────────────────────────────────────────
    print(f"{BOLD}Node.js{RESET} (required for MCP filesystem server)")
    try:
        node_ver = subprocess.check_output(["node", "--version"], text=True).strip()
        npm_ver = subprocess.check_output(["npm", "--version"], text=True).strip()
        ok = check(True, f"{node_ver} (npm {npm_ver})", "Node.js not found — MCP filesystem server will fail at runtime")
        all_ok = all_ok and ok
    except FileNotFoundError:
        warn("Node.js not installed. The filesystem MCP server uses `npx` to run on-demand.")
        warn("Install Node.js ≥18 from https://nodejs.org/ or skip the filesystem tool.")
        print()

    # ── 3. Virtual environment ──────────────────────────────────────────────
    print(f"{BOLD}Virtual Environment{RESET}")
    venv_path = os.environ.get("VIRTUAL_ENV", "")
    venv_ok = check(
        bool(venv_path),
        f"Activated: {venv_path}",
        "No virtual environment detected. Create one: `python -m venv venv && source venv/bin/activate`",
    )
    all_ok = all_ok and venv_ok
    print()

    # ── 4. Dependencies ─────────────────────────────────────────────────────
    print(f"{BOLD}Dependencies{RESET}")
    required_pkgs = ["mcp", "openai", "dotenv", "httpx", "requests"]
    deps_ok = True
    for pkg in required_pkgs:
        try:
            mod = __import__(pkg.replace("-", "_"))
            version = getattr(mod, "__version__", "?")
            check(True, f"{pkg} {version}", f"{pkg} not installed — run `pip install -e .`")
        except ImportError:
            warn(f"{pkg} not installed")
            deps_ok = False
    all_ok = all_ok and deps_ok
    print()

    # ── 5. Environment file ─────────────────────────────────────────────────
    print(f"{BOLD}Configuration{RESET}")
    env_file = root / ".env"
    env_exists = check(
        env_file.exists(),
        ".env file found",
        ".env file not found — run `cp .env.example .env` and fill in your API key",
    )
    all_ok = all_ok and env_exists

    if env_file.exists():
        env_keys = {}
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env_keys[key.strip()] = val.strip()

        has_api_key = bool(env_keys.get("OPENROUTER_API_KEY") and env_keys["OPENROUTER_API_KEY"] != "your_openrouter_api_key_here")
        has_llm_config = has_api_key or bool(env_keys.get("OPENAI_API_BASE"))
        check(
            has_llm_config,
            "LLM configuration found (API key or local base URL)",
            "No LLM credentials detected — add OPENROUTER_API_KEY or configure local Ollama in .env",
        )
    all_ok = all_ok and has_llm_config
    print()

    # ── 6. Package installability ───────────────────────────────────────────
    print(f"{BOLD}Package Installability{RESET}")
    has_pyproject = check(
        (root / "pyproject.toml").exists(),
        "pyproject.toml found — `pip install .` will work",
        "No pyproject.toml — the project cannot be installed via pip",
    )
    all_ok = all_ok and has_pyproject
    print()

    # ── Summary ─────────────────────────────────────────────────────────────
    print("=" * 50)
    if all_ok:
        print(f"{GREEN}{BOLD}✅ All checks passed. You're ready to run the agent!{RESET}")
        print(f"\n  Quick start:  {BOLD}python src/agent_cli.py --example{RESET}")
    else:
        print(f"{RED}{BOLD}❌ Some checks failed. Fix the issues above before running the agent.{RESET}")
    print("=" * 50 + "\n")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
