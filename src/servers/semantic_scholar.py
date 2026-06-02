"""
Semantic Scholar MCP Server
Provides tools for searching academic literature with citation metrics.
"""
import httpx
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("SemanticScholar")


@mcp.tool()
def search_semantic_scholar(query: str, year: str = "2020-2024", limit: int = 10) -> str:
    """
    Search Semantic Scholar for academic papers with citation metrics.

    Args:
        query: The search query.
        year: Publication year range (e.g., "2020-2024").
        limit: Maximum number of results to return.

    Returns:
        Formatted string with paper titles, authors, year, citation count, and open access PDF links.
    """
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "year": year,
            "limit": limit,
            "fields": "title,authors,year,citationCount,openAccessPdf,abstract"
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for paper in data.get("data", []):
            authors = ", ".join([a["name"] for a in paper.get("authors", [])])
            pdf_link = paper.get("openAccessPdf", {}).get("url", "No OA PDF")
            citations = paper.get("citationCount", 0)
            abstract = paper.get("abstract", "No abstract available")

            results.append(
                f"Title: {paper.get('title')}\n"
                f"Authors: {authors}\n"
                f"Year: {paper.get('year')} | Citations: {citations}\n"
                f"PDF: {pdf_link}\n"
                f"Abstract: {abstract}\n"
                f"{'-' * 40}"
            )

        return "\n".join(results) if results else "No papers found matching the criteria."
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return f"Error searching Semantic Scholar: {str(e)}"


if __name__ == "__main__":
    mcp.run()