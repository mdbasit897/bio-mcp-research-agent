#  Bio MCP Research Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Enabled-green.svg)](https://modelcontextprotocol.io/)

An open-source, production-ready Model Context Protocol (MCP) agent designed to automate rigorous, systematic literature reviews for biomedical research. Initially architected for **non-invasive glucose monitoring** research, this modular framework seamlessly integrates advanced LLMs (like Qwen via OpenRouter or local Ollama) with live academic databases (PubMed, Semantic Scholar) and local file systems.

## System Architecture

The agent operates on a client-server MCP architecture:
1. **Orchestrator (`agent.py`)**: Manages the LLM context, parses tool calls, and routes execution.
2. **MCP Servers (`src/servers/`)**: Independent, stateless processes exposing specific capabilities:
   - `pubmed_server.py`: Queries NCBI E-utilities for structured biomedical metadata.
   - `semantic_scholar.py`: Queries the Semantic Scholar API for citation graphs and open-access PDFs.
   - `filesystem`: Official MCP filesystem server for reading/writing research matrices locally.
3. **LLM Backend**: Connects via OpenAI-compatible API (OpenRouter for Qwen, or local Ollama).

## Prerequisites

- **Python 3.10+**
- **Node.js & npm** (Required for the official `@modelcontextprotocol/server-filesystem`)
- An API Key from [OpenRouter](https://openrouter.ai/) (or a local Ollama installation)

## Installation

### Quick Start (Recommended)

```bash
git clone https://github.com/mdbasit897/bio-mcp-research-agent.git
cd bio-mcp-research-agent
python -m venv venv && source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -e ".[dev]"                           # Installs app + dev deps in one command
```

> **Note:** This project also requires **Node.js** (≥18) for the `@modelcontextprotocol/server-filesystem` MCP server.
> Verify with `node --version && npm --version`.

### Manual Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mdbasit897/bio-mcp-research-agent.git
   cd bio-mcp-research-agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

##  Environment Configuration

**Never commit your API keys.** Copy the example environment file and populate it with your credentials:

```bash
cp .env.example .env
```

Edit `.env` to include your OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen-2.5-coder-32b-instruct
```
*(Note: To use a local model, comment out the OpenRouter variables and uncomment the Ollama variables in `.env`)*

## Makefile

A `Makefile` is included for common tasks:

```bash
make install    # Set up venv and install deps
make test       # Run tests with coverage
make lint       # Run flake8
make typecheck  # Run mypy
make clean      # Remove build artifacts
```

## 💻 Usage

The Bio MCP Research Agent is designed for **biomedical researchers** who need to conduct systematic literature reviews efficiently. No coding required!

### Quick Start Options

#### 1. **Interactive Mode** (Recommended for first-time users)
```bash
python src/agent.py
```
You'll be guided through selecting a template and entering your research topic.

#### 2. **Use a Pre-built Template** (Fastest workflow)
```bash
# Systematic literature review
python src/agent.py --template systematic_review --topic "non-invasive glucose monitoring PPG machine learning"

# Meta-analysis data extraction
python src/agent.py -t meta_analysis -T "metformin cardiovascular outcomes type 2 diabetes"

# Research gap analysis for grant proposals
python src/agent.py -t gap_analysis -T "CRISPR gene editing off-target effects"

# Reproducibility audit
python src/agent.py -t reproducibility_check -T "deep learning medical imaging diagnostics"

# Clinical translation roadmap
python src/agent.py -t clinical_translation -T "continuous glucose monitor artificial pancreas"
```

#### 3. **Custom Prompt** (Maximum flexibility)
```bash
python src/agent.py --custom "
Act as a biomedical expert. Search PubMed for recent papers on diabetic retinopathy AI detection.
Extract sensitivity, specificity, and AUC values. Save results to research_outputs/dr_ai.md
"
```

#### 4. **List Available Templates**
```bash
python src/agent.py --list-templates
```

### Available Templates

| Template | Use Case | Output |
|----------|----------|--------|
| `systematic_review` | PhD proposals, grant applications, paper introductions | Structured summary with gaps & future directions |
| `meta_analysis` | Preparing data for statistical meta-analysis | CSV-ready table with effect sizes |
| `gap_analysis` | Identifying research opportunities for R01 grants | Prioritized gap list + Specific Aims draft |
| `reproducibility_check` | Auditing computational studies | Reproducibility scores & recommendations |
| `clinical_translation` | Evaluating path-to-clinic for technologies | TRL assessment + investor summary |

### Output Files

All research outputs are automatically saved to `research_outputs/` directory with timestamps:
- Markdown files (`.md`) with structured summaries
- Tables, figures (as text), and synthesis narratives
- Ready for inclusion in proposals, papers, or presentations

### Example Workflow

```bash
# Step 1: Run a systematic review
python src/agent.py -t systematic_review -T "wearable ECG arrhythmia detection deep learning"

# Step 2: Check the generated output
cat research_outputs/systematic_review_20260607_143022.md

# Step 3: Use the output in your PhD proposal or paper
```

## Contributing

Contributions are highly welcome, especially from the biomedical AI and reproducibility communities!
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-database-mcp`).
3. Commit your changes (`git commit -m 'Add IEEE Xplore MCP server'`).
4. Push to the branch (`git push origin feature/new-database-mcp`).
5. Open a Pull Request.

Please ensure all new MCP servers include comprehensive docstrings and type hints.


##  License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
