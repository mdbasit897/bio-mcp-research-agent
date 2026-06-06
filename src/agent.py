"""
MCP Research Agent Orchestrator
Connects Qwen (via OpenRouter or local Ollama) to MCP servers for automated literature review.
"""
import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables securely
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize OpenAI-compatible client (Works with OpenRouter or Ollama)
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY", "ollama"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "http://localhost:11434/v1"),
    default_headers={
        "HTTP-Referer": "https://github.com/mdbasit897/bio-mcp-research-agent",
        "X-Title": "Bio MCP Research Agent"
    }
)
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct")


async def run_research_agent(prompt: str):
    """
    Executes the research agent workflow: connects to MCP servers,
    routes tool calls to Qwen, and synthesizes the final output.
    """
    # Define MCP server configurations
    servers = {
        "pubmed": StdioServerParameters(
            command="python",
            args=["src/servers/pubmed_server.py"]
        ),
        "semantic_scholar": StdioServerParameters(
            command="python",
            args=["src/servers/semantic_scholar.py"]
        ),
        "filesystem": StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()]
        )
    }

    logger.info(" Initializing MCP server connections...")

    # Context managers to handle server lifecycles
    async with stdio_client(servers["pubmed"]) as (pubmed_r, pubmed_w), \
            stdio_client(servers["semantic_scholar"]) as (ss_r, ss_w), \
            stdio_client(servers["filesystem"]) as (fs_r, fs_w):

        async with ClientSession(pubmed_r, pubmed_w) as pubmed_session, \
                ClientSession(ss_r, ss_w) as ss_session, \
                ClientSession(fs_r, fs_w) as fs_session:

            await pubmed_session.initialize()
            await ss_session.initialize()
            await fs_session.initialize()
            logger.info("✅ All MCP servers connected and initialized.")

            # 1. Gather all available tools from the servers
            pubmed_tools = await pubmed_session.list_tools()
            ss_tools = await ss_session.list_tools()
            fs_tools = await fs_session.list_tools()

            all_tools = [
                {"type": "function", "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }} for tool in (pubmed_tools.tools + ss_tools.tools + fs_tools.tools)
            ]

            # 2. Initial prompt to Qwen
            messages = [{"role": "user", "content": prompt}]
            logger.info(f" Querying Qwen ({MODEL_NAME})...")

            max_iterations = 5
            response = None
            for iteration in range(max_iterations):
                response = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=all_tools,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message
                messages.append(assistant_message)

                # 3. Check for tool calls
                if not assistant_message.tool_calls:
                    # No more tools needed, we have the final answer
                    break

                # 4. Execute tool calls sequentially
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    logger.info(f" Executing tool: {func_name}")

                    # Route to the correct session
                    if func_name in ["search_pubmed", "fetch_pubmed_abstracts"]:
                        session = pubmed_session
                    elif func_name == "search_semantic_scholar":
                        session = ss_session
                    else:
                        session = fs_session

                    try:
                        result = await session.call_tool(func_name, func_args)
                        result_content = str(result.content)
                    except Exception as e:
                        result_content = f"Error executing tool {func_name}: {str(e)}"
                        logger.error(result_content)

                    # Feed the tool result back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_content
                    })

            # 5. Output the final synthesized response
            logger.info(" Final synthesis complete.")
            print("\n" + "=" * 60)
            print(" RESEARCH AGENT OUTPUT:")
            print("=" * 60)
            if response and response.choices and response.choices[0].message:
                print(response.choices[0].message.content)
            else:
                print("No response content available")
            print("=" * 60 + "\n")

if __name__ == "__main__":
    # === CUSTOM PROMPT SECTION ===
    # Replace this with your own research prompt
    custom_prompt = """
    Act as an expert biomedical AI researcher.
    1. Use the `search_pubmed` tool to find 5 recent papers (2020-2024) on "non-invasive glucose monitoring PPG machine learning".
    2. Fetch their abstracts using `fetch_pubmed_abstracts`.
    3. Use the `filesystem` tool to save a structured Markdown summary of their MARD scores and limitations to `research_outputs/glucose_gaps.md`.
    4. Finally, summarize the top 2 methodological gaps for a PhD proposal based on the saved file.
    """

    # Ensure output directory exists
    os.makedirs("research_outputs", exist_ok=True)

    asyncio.run(run_research_agent(custom_prompt))