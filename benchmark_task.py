import re
import kaggle_benchmarks as kbench

@kbench.task(
    name="bio-mcp-research-agent",
    description="Evaluates the ability of an AI agent to perform biomedical literature searches and synthesize findings using MCP tools."
)
def bio_mcp_research_agent(llm) -> None:
    """
    Kaggle Benchmark Task for the Bio MCP Research Agent.
    """
    
    # 1. Define the prompt and system instructions
    prompt = (
        "System: You are a biomedical research assistant. You have access to MCP tools "
        "for PubMed and Semantic Scholar. When asked a question, use these tools to find "
        "evidence before answering. Always cite your sources.\n\n"
        "User: Find recent literature on non-invasive glucose monitoring using PPG and "
        "machine learning. Summarize the limitations."
    )
    
    # 2. Call the model being evaluated
    response = llm.prompt(prompt)
    response_lower = response.lower()
    
    # 3. Evaluate Criteria 1: Did it attempt to search?
    search_indicators = ["search", "found", "paper", "study", "pubmed", "article", "results"]
    kbench.assertions.assert_true(
        any(indicator in response_lower for indicator in search_indicators),
        expectation="Model should attempt to reference search results or papers."
    )
    
    # 4. Evaluate Criteria 2: Structure and Citations
    citation_pattern = r"(\[\d+\]|\([A-Za-z]+,\s*\d{4}\))"
    kbench.assertions.assert_true(
        bool(re.search(citation_pattern, response)),
        expectation="Model should include formal structured citations (e.g., [1] or (Author, Year))."
    )
    
    # 5. Evaluate Criteria 3: Relevance to Prompt
    prompt_words = set(prompt.lower().split())
    response_words = set(response_lower.split())
    overlap = len(prompt_words.intersection(response_words))
    kbench.assertions.assert_true(
        overlap > 5,
        expectation="Response should be highly relevant to the input prompt."
    )
    
    # 6. Evaluate Criteria 4: No Hallucination Flags
    kbench.assertions.assert_true(
        "cannot access" not in response_lower and "no internet" not in response_lower,
        expectation="Model should not report an inability to access tools."
    )
