# MCP Research Agent Usage Guide

## Quick Start

The MCP Research Agent allows you to conduct automated literature reviews using AI-powered tools for PubMed, Semantic Scholar, and filesystem operations.

## Installation & Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=z-ai/glm-4.5-air:free
```

## Usage Methods

### Method 1: Direct Prompt (Simple)
```bash
python src/agent.py
```
- Edit the `custom_prompt` variable directly in `src/agent.py`
- Most straightforward for quick tests

### Method 2: Command Line Arguments (Recommended)
```bash
# Using a direct prompt string
python src/agent_cli.py --prompt "Your research prompt here"

# Using a prompt file
python src/agent_cli.py --file prompts/your_prompt.txt

# Using the built-in example
python src/agent_cli.py --example
```

### Method 3: Custom Python Script
```python
import asyncio
from src.agent import run_research_agent

my_prompt = """
Act as an expert researcher.
1. Use search_pubmed to find papers on "your topic"
2. Fetch abstracts using fetch_pubmed_abstracts
3. Save results to research_outputs/your_analysis.md
"""

asyncio.run(run_research_agent(my_prompt))
```

## Available Tools

### PubMed Tools
- `search_pubmed`: Search PubMed for papers
- `fetch_pubmed_abstracts`: Get abstracts for specific PMIDs

### Semantic Scholar Tools  
- `search_semantic_scholar`: Search Semantic Scholar database

### Filesystem Tools
- `filesystem`: Save results, create files, manage directories

## Example Prompts

The `prompts/` directory contains example prompts:
- `cancer_research.txt` - Oncology AI research
- `cardiovascular_research.txt` - Cardiovascular AI analysis

## Custom Prompt Templates

### Basic Research Template
```
Act as an expert [field] AI researcher.

1. Use `search_pubmed` to find [number] papers (year-range) on "[search terms]"
2. Fetch their abstracts using `fetch_pubmed_abstracts`
3. Use the `filesystem` tool to save analysis to `research_outputs/your_analysis.md`
4. Summarize key findings and limitations
```

### Advanced Research Template
```
Act as an expert [field] researcher.

1. Use `search_pubmed` to find papers on "[topic A]"
2. Use `search_semantic_scholar` to find papers on "[topic B]"
3. Fetch abstracts from both sources
4. Use filesystem to create comparative analysis
5. Identify trends, gaps, and future directions
```

## Output Location

All results are saved to `research_outputs/` directory:
- Research analysis files
- Comparative tables
- Summaries and reports

## Tips for Effective Prompts

1. **Be specific** about time ranges (e.g., "2020-2024")
2. **Define exact output format** you want
3. **Specify file locations** for saved results
4. **Break down complex tasks** into numbered steps
5. **Include both search and analysis** phases

## Troubleshooting

- **Network issues**: Check internet connection for PubMed/SS API access
- **API limits**: Results may be limited due to rate limiting
- **Output format**: Specify exact format requirements in your prompt