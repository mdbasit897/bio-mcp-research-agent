# Contributing to Bio MCP Research Agent

Thank you for your interest in contributing! This project welcomes contributions from the biomedical AI, reproducibility, and open science communities.

## Ways to Contribute

### 1. Add New MCP Servers
We encourage adding support for additional databases and tools:
- IEEE Xplore (for engineering/tech literature)
- arXiv API (for preprints)
- ClinicalTrials.gov (for clinical trial data)
- Europe PMC
- Cochrane Library
- Scopus/Web of Science (if API access available)

**Guidelines:**
- Follow the existing server pattern in `src/servers/`
- Include comprehensive docstrings
- Add type hints
- Test with real API calls
- Document rate limits and authentication

### 2. Improve Prompt Templates
Have expertise in a specific research methodology? Add or refine templates:
- Network meta-analysis
- Umbrella reviews
- Living systematic reviews
- Domain-specific workflows (genomics, proteomics, medical imaging, etc.)

### 3. Enhance Documentation
- Add tutorials for specific use cases
- Create video walkthroughs
- Translate documentation to other languages
- Add FAQ section

### 4. Bug Reports & Feature Requests
Use GitHub Issues to report:
- Bugs (include Python version, OS, error traceback)
- Feature requests (explain use case)
- Documentation improvements

## Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/bio-mcp-research-agent.git
cd bio-mcp-research-agent

# Set up development environment
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# Run tests
make test

# Run linting
make lint
make typecheck
```

## Code Style

- **Type Hints**: Required for all functions
- **Docstrings**: Google-style for all public functions/classes
- **Formatting**: Follow PEP 8
- **Error Handling**: Graceful degradation when APIs fail
- **Logging**: Use appropriate log levels (INFO for progress, ERROR for failures)

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Ensure all tests pass (`make test`)
4. Update documentation if needed
5. Submit PR with description of changes
6. Respond to review feedback

## Adding a New MCP Server (Example)

```python
"""
IEEE Xplore MCP Server
Provides search and abstract retrieval from IEEE Xplore API.
"""
from mcp.server import Server
import requests

server = Server("ieee_xplore")

@server.tool()
def search_ieee(query: str, max_results: int = 10) -> list:
    """
    Search IEEE Xplore for technical literature.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)
    
    Returns:
        List of paper metadata (title, authors, abstract, DOI, URL)
    """
    # Implementation here
    pass
```

## Community Guidelines

- Be respectful and inclusive
- Help newcomers learn the tool
- Cite this project if you use it in publications
- Share your success stories and use cases

## Questions?

Open an issue or contact the maintainers. We're happy to help!

---

**By contributing, you agree that your contributions will be licensed under the MIT License.**
