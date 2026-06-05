# 🚀 Kaggle Benchmarks Local Development - Complete Setup Guide

## For: Bio MCP Research Agent Submission

This guide walks you through setting up, testing, and submitting your **Bio MCP Research Agent** as a Kaggle Benchmark task using the new local development workflow.

---

## 📋 Prerequisites Checklist

- ✅ Python 3.10+ (You have: Python 3.12.10)
- ✅ Node.js & npm (You have: Installed)
- ✅ Kaggle CLI installed (Just installed: v2.2.1)
- ✅ Your `.env` file with API keys (You mentioned you have this)
- ✅ GitHub repository with your code

---

## 🔧 Step 1: Set Up Your Environment

### 1.1 Create Virtual Environment (Recommended)
```bash
cd /workspace
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

### 1.3 Configure Your .env File
Since you already have your correct `.env` file, ensure it's in the `/workspace` directory:

```bash
# Verify your .env exists
ls -la .env

# It should contain:
# OPENROUTER_API_KEY=your_actual_key
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=qwen/qwen-2.5-coder-32b-instruct
```

---

## 🏗️ Step 2: Initialize Kaggle Benchmarks Environment

### 2.1 Run Kaggle Init
```bash
kaggle benchmarks init -y
```

This will:
- Fetch Model Proxy credentials
- Create/update your `.env` with Kaggle-specific variables
- Generate an example benchmark task file

### 2.2 Verify Initialization
```bash
cat .env | grep -E "KAGGLE|MODEL_PROXY"
```

---

## 📝 Step 3: Create Your Kaggle Benchmark Task

Your current `src/agent.py` is an MCP research agent, but for Kaggle Benchmarks, you need to create a **task definition file** that evaluates AI models.

### 3.1 Create a Benchmark Task File

Create a new file `benchmark_task.py`:

```python
"""
Bio MCP Research Agent - Kaggle Benchmark Task
Evaluates AI model capabilities in biomedical literature review
"""

def evaluate_model(response, context):
    """
    Evaluate the model's response against expected criteria.
    
    Args:
        response: The model's generated response
        context: Additional context about the task
    
    Returns:
        dict: Evaluation metrics
    """
    # Example evaluation criteria
    score = 0
    max_score = 100
    
    # Check if response contains key elements
    if response:
        # Criterion 1: Contains PubMed search results
        if "PMID" in response or "PubMed" in response:
            score += 25
        
        # Criterion 2: Structured output
        if any(marker in response for marker in ["##", "**", "1.", "-"]):
            score += 25
        
        # Criterion 3: Mentions specific research gaps
        if any(term in response.lower() for term in ["gap", "limitation", "future"]):
            score += 25
        
        # Criterion 4: Provides actionable insights
        if len(response.split()) > 100:
            score += 25
    
    return {
        "score": score,
        "max_score": max_score,
        "metrics": {
            "has_citations": "PMID" in response if response else False,
            "is_structured": any(marker in response for marker in ["##", "**"]) if response else False,
            "mentions_gaps": any(term in response.lower() for term in ["gap", "limitation"]) if response else False,
            "length_adequate": len(response.split()) > 100 if response else False
        }
    }


def get_task_prompt():
    """Return the prompt that will be sent to models."""
    return """
Act as an expert biomedical AI researcher conducting a systematic literature review.

Your task:
1. Search for recent papers (2020-2024) on "non-invasive glucose monitoring using PPG and machine learning"
2. Identify the top 3 methodological approaches used
3. Summarize the main limitations and research gaps
4. Propose 2 specific directions for future research

Format your response as a structured markdown report with:
- ## Summary
- ## Key Approaches
- ## Limitations & Gaps
- ## Future Directions

Be specific and cite relevant methodologies even if you cannot access real-time databases.
"""


if __name__ == "__main__":
    # This is how the task will be executed
    prompt = get_task_prompt()
    print("Task Prompt:")
    print(prompt)
    print("\n" + "="*60)
    print("Evaluation will be performed on model response using evaluate_model()")
```

### 3.2 Validate Your Task Locally
```bash
# Test your task file syntax
python -m py_compile benchmark_task.py

# Run it locally to see the prompt
python benchmark_task.py
```

---

## 🚀 Step 4: Push Your Task to Kaggle

### 4.1 Push the Task
```bash
kaggle benchmarks tasks push bio-mcp-research-agent -f benchmark_task.py
```

This will:
- Create a new task named `bio-mcp-research-agent`
- Upload your `benchmark_task.py` file
- Return a URL to your task page

**Expected Output:**
```
✓ Task created successfully
🔗 View task: https://www.kaggle.com/benchmarks/tasks/bio-mcp-research-agent
```

### 4.2 Update an Existing Task
If you need to update your task after changes:
```bash
kaggle benchmarks tasks push bio-mcp-research-agent -f benchmark_task.py --wait
```

---

## 🧪 Step 5: Run Your Task Against Models

### 5.1 List Available Models
```bash
kaggle benchmarks tasks models
```

### 5.2 Run Against Specific Models
```bash
# Run against a single model
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4

# Run against multiple models
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4 -m claude-3 -m gemini-pro

# Run and wait for completion (with timeout)
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4 --wait 300
```

### 5.3 Check Task Status
```bash
kaggle benchmarks tasks status bio-mcp-research-agent
```

---

## 📥 Step 6: Download Results

### 6.1 Download All Results
```bash
kaggle benchmarks tasks download bio-mcp-research-agent -o ./results
```

### 6.2 Download for Specific Model
```bash
kaggle benchmarks tasks download bio-mcp-research-agent -m gpt-4 -o ./results/gpt4
```

### 6.3 Include Source Notebooks
```bash
kaggle benchmarks tasks download bio-mcp-research-agent -o ./results -s
```

---

## 🤖 Optional: Use AI Agent with Skills

As mentioned in the Kaggle announcement, you can use AI coding agents:

### Install the Write-Kaggle-Benchmarks Skill
```bash
npx skills add Kaggle/kaggle-skills --skill write-kaggle-benchmarks
```

### Then Ask Your Agent
Tell your AI agent (Cursor, Claude Code, etc.):
> "Using the write-kaggle-benchmarks skill, create a benchmark task that evaluates AI models on their ability to conduct systematic biomedical literature reviews. The task should test: 1) Search strategy formulation, 2) Critical analysis of limitations, 3) Identification of research gaps."

---

## 🧪 Testing Your Setup

### Quick Local Test
```bash
# Test that your agent runs locally
python src/agent_cli.py --example
```

### Run Unit Tests
```bash
pytest tests/unit/ -v
```

### Check Coverage
```bash
pytest tests/unit/ --cov=src --cov-report=html
```

---

## 📊 Expected Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Kaggle Benchmarks Workflow                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INIT                                                     │
│     $ kaggle benchmarks init -y                             │
│                                                              │
│  2. WRITE & VALIDATE                                         │
│     → Create benchmark_task.py                              │
│     $ python -m py_compile benchmark_task.py                │
│                                                              │
│  3. PUSH                                                     │
│     $ kaggle b t push bio-mcp-research-agent -f task.py     │
│                                                              │
│  4. RUN                                                      │
│     $ kaggle b t run bio-mcp-research-agent -m gpt-4        │
│                                                              │
│  5. DOWNLOAD                                                 │
│     $ kaggle b t download bio-mcp-research-agent -o ./out   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Troubleshooting

### Issue: "Not enough values to unpack" Error
**Fix:** This occurs in `src/agent.py` when MCP servers fail to connect. Add error handling:
```python
try:
    async with stdio_client(servers["pubmed"]) as (pubmed_r, pubmed_w):
        # ... rest of code
except Exception as e:
    logger.error(f"Server connection failed: {e}")
    raise
```

### Issue: API Rate Limiting
**Solution:** 
- Use cached responses in tests
- Add delays between API calls
- Use mock data for development

### Issue: Kaggle CLI Authentication
**Fix:**
```bash
kaggle auth init
# Follow prompts to enter your Kaggle username and API token
```

---

## 🎯 Submission Checklist for Kaggle

Before July 1st submission deadline:

- [ ] Task file created and validated locally
- [ ] Task pushed to Kaggle Benchmarks
- [ ] Task run against at least 2 different models
- [ ] Results downloaded and verified
- [ ] Post on X/Twitter or LinkedIn with:
  - Your task name and URL
  - Your workflow screenshot
  - Tag @kaggle
  - Use hashtag #KaggleBenchmarks

---

## 📚 Additional Resources

- **Kaggle CLI Docs:** https://github.com/Kaggle/kaggle-cli
- **Write-Kaggle-Benchmarks Skill:** https://github.com/Kaggle/kaggle-skills
- **Blog Post:** https://www.kaggle.com/discussions/product-feedback/... (check Kaggle blog)
- **YouTube Demo:** Search "Kaggle Benchmarks local development"

---

## 💡 Pro Tips

1. **Start Simple:** Begin with a basic evaluation task, then iterate
2. **Test Locally First:** Always validate your task file before pushing
3. **Use Verbose Mode:** Add `-v` flag to see detailed execution logs
4. **Save Your Work:** Keep versions of your task files in Git
5. **Monitor Costs:** Running against multiple models may incur API costs

---

**Good luck with your Kaggle Benchmarks submission! 🚀**

For questions, check the Kaggle forums or reply to this guide.
