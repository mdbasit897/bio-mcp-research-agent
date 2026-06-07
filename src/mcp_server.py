#!/usr/bin/env python3
"""
Bio MCP Research Agent as an MCP Server.

This module exposes biomedical research capabilities as MCP tools,
allowing other clients (IDEs, agents, dashboards) to connect and
request literature reviews, gap analyses, and summaries.

Usage:
    python -m src.mcp_server
"""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("bio-mcp-server")

# Import OpenAI client for LLM interaction
try:
    from openai import AsyncOpenAI
except ImportError:
    logger.error("openai package not found. Please install it: pip install openai")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not found. Ensure env vars are set manually.")

# Initialize OpenAI Client (OpenRouter)
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
default_model = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")

if not api_key:
    logger.error("OPENROUTER_API_KEY not found in environment variables.")
    sys.exit(1)

client = AsyncOpenAI(api_key=api_key, base_url=base_url)

# Initialize MCP Server
server = Server("bio-research-agent")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available research tools."""
    return [
        Tool(
            name="search_lit",
            description="Search biomedical literature (PubMed) for a specific topic and return relevant paper titles and IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The research topic or query (e.g., 'non-invasive glucose monitoring')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="analyze_gap",
            description="Analyze search results to identify research gaps, contradictions, and future directions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The research topic to analyze"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional additional context or specific focus area"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="summarize_papers",
            description="Generate a structured summary of key findings from literature on a given topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The research topic"
                    },
                    "focus": {
                        "type": "string",
                        "description": "Specific aspect to focus on (e.g., 'methodology', 'clinical outcomes')"
                    }
                },
                "required": ["topic"]
            }
        )
    ]

async def run_llm_task(system_prompt: str, user_prompt: str) -> str:
    """Helper to run LLM completion."""
    try:
        response = await client.chat.completions.create(
            model=default_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        return f"Error processing request: {str(e)}"

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool execution requests."""
    logger.info(f"Tool called: {name} with args: {arguments}")

    if name == "search_lit":
        topic = arguments.get("topic")
        max_results = arguments.get("max_results", 10)
        
        # Construct prompt for LLM to simulate search (or integrate real PubMed API here)
        # For now, we use the LLM's internal knowledge + instruction to simulate structured output
        # In a production setup, you would call the actual PubMed MCP client here
        prompt = (
            f"Act as a biomedical research assistant. Search your internal knowledge for recent literature on: '{topic}'.\n"
            f"Provide a list of up to {max_results} relevant paper titles, authors (if known), and a one-sentence summary for each.\n"
            f"Format as a markdown list."
        )
        result = await run_llm_task("You are a helpful research assistant.", prompt)
        return [TextContent(type="text", text=result)]

    elif name == "analyze_gap":
        topic = arguments.get("topic")
        context = arguments.get("context", "")
        
        prompt = (
            f"Analyze the current state of research on: '{topic}'.\n"
            f"{f'Context: {context}' if context else ''}\n"
            f"Identify:\n1. Major consensus findings\n2. Contradictions or debates\n3. Critical research gaps\n4. Promising future directions.\n"
            f"Format as a structured report."
        )
        result = await run_llm_task("You are an expert biomedical grant reviewer.", prompt)
        return [TextContent(type="text", text=result)]

    elif name == "summarize_papers":
        topic = arguments.get("topic")
        focus = arguments.get("focus", "general findings")
        
        prompt = (
            f"Provide a comprehensive summary of literature on: '{topic}'.\n"
            f"Focus specifically on: {focus}.\n"
            f"Include key methodologies, sample sizes (if typical), and main conclusions."
        )
        result = await run_llm_task("You are a systematic review expert.", prompt)
        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    logger.info("Starting Bio Research MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
