"""
PubMed MCP Server
Provides tools for searching and retrieving biomedical literature via NCBI E-utilities.
"""
import requests
import xml.etree.ElementTree as ET
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("PubMed")


@mcp.tool()
def search_pubmed(query: str, max_results: int = 10) -> str:
    """
    Search PubMed for biomedical literature.

    Args:
        query: The search string (supports MeSH terms and Boolean operators).
        max_results: Maximum number of PMIDs to return (default: 10).

    Returns:
        A string containing the total count and a comma-separated list of PMIDs.
    """
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        pmids = data.get('esearchresult', {}).get('idlist', [])
        count = data.get('esearchresult', {}).get('count', '0')

        logger.info(f"PubMed search found {count} results for query: {query}")
        return f"Found {count} total results. Retrieved PMIDs: {', '.join(pmids)}"
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        return f"Error searching PubMed: {str(e)}"


@mcp.tool()
def fetch_pubmed_abstracts(pmids: str) -> str:
    """
    Fetch titles, authors, and abstracts for a comma-separated list of PMIDs.

    Args:
        pmids: Comma-separated string of PubMed IDs (e.g., "12345678,87654321").

    Returns:
        A formatted string containing the metadata and abstracts of the requested papers.
    """
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmids}&retmode=xml"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        results = []

        for article in root.findall('.//PubmedArticle'):
            try:
                title = article.find('.//ArticleTitle')
                title_text = title.text.strip() if title is not None and title.text else "No Title"

                journal = article.find('.//Journal/Title')
                journal_text = journal.text.strip() if journal is not None and journal.text else "Unknown Journal"

                year = article.find('.//PubDate/Year')
                year_text = year.text.strip() if year is not None and year.text else "Unknown Year"

                abstract = article.find('.//Abstract/AbstractText')
                abstract_text = abstract.text.strip() if abstract is not None and abstract.text else "No Abstract"

                results.append(
                    f"Title: {title_text}\nJournal: {journal_text} ({year_text})\nAbstract: {abstract_text}\n{'-' * 40}")
            except Exception as parse_err:
                logger.warning(f"Failed to parse article: {parse_err}")
                continue

        return "\n".join(results) if results else "No details found for the provided PMIDs."
    except Exception as e:
        logger.error(f"PubMed fetch failed: {e}")
        return f"Error fetching abstracts: {str(e)}"


if __name__ == "__main__":
    mcp.run()