"""
MCP Research Agent Orchestrator
Connects Qwen (via OpenRouter or local Ollama) to MCP servers for automated literature review.

Designed for biomedical researchers to perform systematic literature reviews,
extract key metrics, and generate structured research outputs.
"""
import os
import sys
import json
import asyncio
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
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


# Pre-built prompt templates for common biomedical research tasks
PROMPT_TEMPLATES = {
    "systematic_review": """
Act as an expert biomedical AI researcher conducting a systematic literature review.

Research Topic: {topic}

Execute the following workflow:
1. **Search**: Use `search_pubmed` to find 10-15 recent papers (2020-2024) on "{topic}".
2. **Extract**: Use `fetch_pubmed_abstracts` to retrieve full abstracts for all found papers.
3. **Analyze**: For each paper, identify:
   - Study design and population
   - Key methodology/technology used
   - Main outcomes and metrics (e.g., accuracy, MARD, sensitivity, specificity)
   - Stated limitations and future work
4. **Persist**: Use the `filesystem` tool to save a structured Markdown file at `research_outputs/{filename}` containing:
   - A summary table of all papers
   - Key findings synthesis
   - Methodological gaps identified
5. **Synthesize**: Provide a concise 400-word summary highlighting:
   - Current state of the field
   - Top 3 unresolved challenges
   - Recommended directions for future research

Format your output for inclusion in a PhD proposal or grant application.
""",

    "meta_analysis": """
Act as a biostatistician and domain expert preparing data for a meta-analysis.

Research Question: {topic}

Execute the following workflow:
1. **Search**: Use `search_pubmed` to find all relevant studies (2015-2024) on "{topic}".
2. **Extract**: Use `fetch_pubmed_abstracts` to get complete abstracts.
3. **Extract Data**: For each study, extract:
   - Sample size and population characteristics
   - Intervention/exposure details
   - Control/comparator information
   - Outcome measures and effect sizes (with confidence intervals if available)
   - Statistical methods used
4. **Persist**: Save a structured CSV-ready table at `research_outputs/{filename}` with columns:
   Author, Year, N, Population, Intervention, Comparator, Primary_Outcome, Effect_Size, CI_Lower, CI_Upper, P_value, Limitations
5. **Quality Assessment**: Evaluate each study for:
   - Risk of bias (selection, performance, detection, attrition, reporting)
   - Applicability to the research question
6. **Synthesize**: Provide a narrative summary of heterogeneity sources and recommendations for meta-analytic approach.
""",

    "gap_analysis": """
Act as a senior PI identifying research gaps for a new grant proposal.

Domain: {topic}

Execute the following workflow:
1. **Search**: Use `search_pubmed` to find 20+ influential papers on "{topic}" from the past 5 years.
2. **Extract**: Use `fetch_pubmed_abstracts` for detailed analysis.
3. **Map the Landscape**: Categorize papers by:
   - Methodological approach
   - Population studied
   - Key findings
   - Funded by (if mentioned)
4. **Identify Gaps**: Systematically identify:
   - Understudied populations or conditions
   - Methodological limitations across studies
   - Contradictory findings needing resolution
   - Emerging technologies not yet applied
   - Translational barriers
5. **Persist**: Save a comprehensive gap analysis at `research_outputs/{filename}` including:
   - Visual landscape map (as text diagram)
   - Prioritized gap list with justification
   - Specific aims draft for R01-style proposal
6. **Synthesize**: Write a 500-word "Significance and Innovation" section suitable for NIH grant submission.
""",

    "reproducibility_check": """
Act as a reproducibility auditor for computational biomedical research.

Target Domain: {topic}

Execute the following workflow:
1. **Search**: Use `search_pubmed` to find 10 recent computational/AI studies on "{topic}".
2. **Extract**: Use `fetch_pubmed_abstracts` to examine methods sections.
3. **Assess Reproducibility**: For each paper, evaluate:
   - Code availability (GitHub, Zenodo, etc.)
   - Data availability statements
   - Hyperparameter reporting completeness
   - Statistical power justification
   - Validation methodology (train/test split, cross-validation, external validation)
   - Performance metric appropriateness
4. **Score**: Assign a reproducibility score (1-5) for each paper with justification.
5. **Persist**: Save a detailed audit report at `research_outputs/{filename}` with:
   - Individual paper assessments
   - Field-wide reproducibility trends
   - Recommendations for improving standards
6. **Synthesize**: Provide actionable recommendations for researchers in this field to improve reproducibility and transparency.
""",

    "clinical_translation": """
Act as a translational medicine expert evaluating path-to-clinic for emerging technologies.

Technology Area: {topic}

Execute the following workflow:
1. **Search**: Use `search_pubmed` to find studies on "{topic}" with emphasis on clinical validation.
2. **Extract**: Use `fetch_pubmed_abstracts` for detailed review.
3. **TRL Assessment**: For each technology/study, determine:
   - Current Technology Readiness Level (TRL 1-9)
   - Regulatory pathway considerations (FDA Class II/III, CE mark, etc.)
   - Clinical evidence strength (in silico, in vitro, animal, human pilot, RCT)
   - Manufacturing scalability issues mentioned
   - Cost-effectiveness data if available
4. **Barrier Analysis**: Identify:
   - Technical hurdles remaining
   - Regulatory challenges
   - Reimbursement landscape
   - Clinical adoption barriers
5. **Persist**: Save a translation roadmap at `research_outputs/{filename}` including:
   - TRL progression timeline
   - Critical path items
   - Stakeholder engagement strategy
6. **Synthesize**: Write an executive summary for potential investors or technology transfer office.
"""
}


def list_templates():
    """Display available prompt templates."""
    print("\nAvailable Research Prompt Templates:")
    print("=" * 60)
    for key, template in PROMPT_TEMPLATES.items():
        # Extract first line as description
        first_line = template.strip().split('\n')[0]
        print(f"\n  {key.upper().replace('_', ' ')}")
        print(f"    {first_line}")
    print("\n" + "=" * 60)
    print("\nUsage: python src/agent.py --template <template_name> --topic 'Your research topic'")
    print("   or: python src/agent.py --custom 'Your custom prompt'")
    print("   or: python src/agent.py  (interactive mode)")
    print("=" * 60 + "\n")


def build_prompt(template_name: Optional[str], topic: Optional[str], custom_prompt: Optional[str]) -> str:
    """Build the final prompt from template, topic, or custom input."""
    
    if custom_prompt:
        return custom_prompt
    
    if template_name:
        template_name = template_name.lower().strip()
        if template_name not in PROMPT_TEMPLATES:
            logger.error(f"Template '{template_name}' not found. Available templates: {list(PROMPT_TEMPLATES.keys())}")
            print("\nAvailable templates:")
            for t in PROMPT_TEMPLATES.keys():
                print(f"  - {t}")
            sys.exit(1)
        
        topic = topic or "biomedical research"
        filename = f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        return PROMPT_TEMPLATES[template_name].format(topic=topic, filename=filename)
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("  BIO MCP RESEARCH AGENT - INTERACTIVE MODE")
    print("=" * 60)
    print("\nThis tool helps you conduct systematic literature reviews using AI.")
    print("You can use a pre-built template or write your own custom prompt.\n")
    
    # Show template options
    print("Available templates:")
    for i, (key, template) in enumerate(PROMPT_TEMPLATES.items(), 1):
        first_line = template.strip().split('\n')[0]
        print(f"  {i}. {key.upper().replace('_', ' ')} - {first_line}")
    print(f"  {len(PROMPT_TEMPLATES) + 1}. CUSTOM - Write your own prompt")
    
    while True:
        try:
            choice = input(f"\nSelect template (1-{len(PROMPT_TEMPLATES) + 1}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(PROMPT_TEMPLATES) + 1:
                break
            print(f"Please enter a number between 1 and {len(PROMPT_TEMPLATES) + 1}")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)
    
    choice_idx = int(choice) - 1
    
    if choice_idx == len(PROMPT_TEMPLATES):
        # Custom prompt
        print("\nEnter your research prompt (type 'DONE' on a new line when finished):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'DONE':
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
        return '\n'.join(lines)
    
    # Selected template
    template_key = list(PROMPT_TEMPLATES.keys())[choice_idx]
    topic = input(f"\nEnter your specific research topic: ").strip()
    if not topic:
        topic = "biomedical research"
    
    filename = f"{template_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    return PROMPT_TEMPLATES[template_key].format(topic=topic, filename=filename)


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
            logger.info("All MCP servers connected and initialized.")

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
    # Parse command line arguments - Simple interface for researchers
    parser = argparse.ArgumentParser(
        description="""Bio MCP Research Agent - Automated systematic literature review for biomedical research.

Just type your research topic or question and the agent will handle everything!
        
Examples:
  python src/agent.py                                    # Interactive mode
  python src/agent.py "non-invasive glucose monitoring"  # Quick research on a topic
  python src/agent.py "What are the latest advances in CRISPR off-target detection?"
  python src/agent.py --list-templates                   # Show available templates
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "topic",
        nargs="?",
        type=str,
        default=None,
        help="Your research topic or question (e.g., 'wearable ECG arrhythmia detection')"
    )
    parser.add_argument(
        "-t", "--template",
        type=str,
        help="Use a pre-built template (systematic_review, meta_analysis, gap_analysis, reproducibility_check, clinical_translation)"
    )
    parser.add_argument(
        "-T", "--topic-flag",
        dest="topic_flag",
        type=str,
        help="Research topic to use with template (alternative to positional argument)"
    )
    parser.add_argument(
        "-c", "--custom",
        type=str,
        help="Custom research prompt (bypasses templates)"
    )
    parser.add_argument(
        "-l", "--list-templates",
        action="store_true",
        help="List all available prompt templates and exit"
    )
    
    args = parser.parse_args()
    
    # Handle list templates option
    if args.list_templates:
        list_templates()
        sys.exit(0)
    
    # Determine the topic from various sources
    topic = args.topic or args.topic_flag
    
    # Build the prompt based on input
    if args.custom:
        prompt = args.custom
    elif args.template:
        prompt = build_prompt(args.template, topic, None)
    elif topic:
        # User provided a simple topic - use systematic_review template by default
        logger.info(f"Researching: {topic}")
        prompt = build_prompt("systematic_review", topic, None)
    else:
        # Interactive mode - no arguments provided
        prompt = build_prompt(None, None, None)
    
    # Ensure output directory exists
    os.makedirs("research_outputs", exist_ok=True)
    
    logger.info("Starting research agent...")
    asyncio.run(run_research_agent(prompt))