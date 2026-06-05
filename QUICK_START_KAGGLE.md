# 🚀 Quick Start: Kaggle Benchmarks Submission

## For: Bio MCP Research Agent

### ✅ What's Ready
- **Kaggle CLI**: Installed (v2.2.1)
- **Python**: 3.12.10 ✓
- **Node.js**: Installed ✓
- **Benchmark Task File**: `benchmark_task.py` created and validated ✓
- **Unit Tests**: 29/29 passing (58.37% coverage) ✓

---

## 🔑 Step 1: Create Your .env File

Since you mentioned you have your correct `.env` file, create it in `/workspace`:

```bash
cat > /workspace/.env << 'EOF'
# OpenRouter Configuration
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=qwen/qwen-2.5-coder-32b-instruct
EOF
```

**Replace `your_actual_api_key_here` with your real OpenRouter API key.**

---

## 🏗️ Step 2: Initialize Kaggle Environment

```bash
cd /workspace
kaggle benchmarks init -y
```

This will:
- Fetch Model Proxy credentials from Kaggle
- Add Kaggle-specific environment variables to your `.env`
- Generate an example task file (`example_task.py`)

**Verify:**
```bash
grep -E "KAGGLE|MODEL_PROXY" .env
```

---

## 📝 Step 3: Review Your Benchmark Task

Your task file is ready at `/workspace/benchmark_task.py`

**Test it locally:**
```bash
python benchmark_task.py
```

**Expected output:**
```
======================================================================
BIO MCP RESEARCH AGENT - KAGGLE BENCHMARK TASK
======================================================================
📊 EVALUATION RESULTS:
   Score: 90/100 (90.0%)
   ...
```

---

## 🚀 Step 4: Push to Kaggle

**First-time push:**
```bash
kaggle benchmarks tasks push bio-mcp-research-agent -f benchmark_task.py
```

**Expected output:**
```
✓ Task created successfully
🔗 View task: https://www.kaggle.com/benchmarks/tasks/bio-mcp-research-agent
```

**Update existing task:**
```bash
kaggle benchmarks tasks push bio-mcp-research-agent -f benchmark_task.py --wait
```

---

## 🧪 Step 5: Run Against Models

**List available models:**
```bash
kaggle benchmarks tasks models
```

**Run against specific models:**
```bash
# Single model
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4

# Multiple models
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4 -m claude-3-sonnet

# Run and wait (5 minute timeout)
kaggle benchmarks tasks run bio-mcp-research-agent -m gpt-4 --wait 300
```

**Check status:**
```bash
kaggle benchmarks tasks status bio-mcp-research-agent
```

---

## 📥 Step 6: Download Results

```bash
# Download all results
kaggle benchmarks tasks download bio-mcp-research-agent -o ./results

# Download for specific model
kaggle benchmarks tasks download bio-mcp-research-agent -m gpt-4 -o ./results/gpt4

# Include source notebooks
kaggle benchmarks tasks download bio-mcp-research-agent -o ./results -s
```

---

## 📊 Complete Workflow Summary

```bash
# 1. Initialize (one-time setup)
kaggle benchmarks init -y

# 2. Validate your task locally
python benchmark_task.py

# 3. Push to Kaggle
kaggle b t push bio-mcp-research-agent -f benchmark_task.py

# 4. Run against models
kaggle b t run bio-mcp-research-agent -m gpt-4 -m claude-3

# 5. Check status
kaggle b t status bio-mcp-research-agent

# 6. Download results
kaggle b t download bio-mcp-research-agent -o ./results
```

---

## ⚠️ Important Notes

### Authentication Required
Before pushing, ensure you're authenticated with Kaggle:

```bash
# Check authentication
kaggle auth init

# Or set environment variables:
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_token
```

Get your API token from: https://www.kaggle.com/settings

### Task Naming
- Task names are normalized to URL-safe slugs
- `bio-mcp-research-agent` becomes `bio-mcp-research-agent`
- Avoid spaces and special characters

### Costs
Running against multiple models may incur API costs depending on the models used.

---

## 🎯 Submission Checklist

Before July 1st deadline:

- [ ] `.env` file created with API keys
- [ ] `kaggle benchmarks init -y` completed
- [ ] Task validated locally (`python benchmark_task.py`)
- [ ] Task pushed to Kaggle
- [ ] Task run against ≥2 models
- [ ] Results downloaded and verified
- [ ] **Social Media Post** (for swag eligibility):
  - Post on X/Twitter or LinkedIn
  - Include task URL and workflow screenshot
  - Tag @kaggle
  - Use #KaggleBenchmarks

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `benchmark_task.py` | Kaggle Benchmark task definition |
| `KAGGLE_BENCHMARKS_SETUP_GUIDE.md` | Detailed setup guide |
| `QUICK_START_KAGGLE.md` | This quick start guide |

---

## 🆘 Troubleshooting

### "Not authenticated" error
```bash
kaggle auth init
# Follow prompts to enter username and API token
```

### "Task already exists" error
Use the same command - it will update the existing task:
```bash
kaggle benchmarks tasks push bio-mcp-research-agent -f benchmark_task.py
```

### "Model not found" error
List available models first:
```bash
kaggle benchmarks tasks models
```

---

## 📚 Resources

- **Full Guide**: See `KAGGLE_BENCHMARKS_SETUP_GUIDE.md`
- **Kaggle CLI Docs**: https://github.com/Kaggle/kaggle-cli
- **Example Task**: `example_task.py` (generated by `kaggle benchmarks init`)

---

**Ready to submit? Start with Step 2!** 🚀
