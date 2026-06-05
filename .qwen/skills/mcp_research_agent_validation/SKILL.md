---
name: mcp_research_agent_validation
description: Comprehensive testing and validation approach for MCP-based research agents
source: auto-skill
extracted_at: '2026-06-05T02:48:45.000Z'
---

# MCP Research Agent Validation Procedure

## Overview
This skill provides a systematic approach to testing and validating MCP (Model Context Protocol) research agents, focusing on biomedical AI applications. The method combines automated testing with manual verification to ensure production readiness.

## Validation Workflow

### Phase 1: Environment Setup Validation
```bash
# Check Python version compatibility
python --version  # Should be 3.10+

# Install core dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio

# Verify critical imports
python -c "
import sys
sys.path.insert(0, 'src')
try:
    import agent
    import servers.pubmed_server
    import servers.semantic_scholar
    print('✅ All core modules import successfully')
except Exception as e:
    print(f'❌ Import failed: {e}')
"
```

### Phase 2: Syntax and Compilation Checks
```bash
# Compile all Python files to check syntax
python -m py_compile src/agent.py src/servers/pubmed_server.py src/servers/semantic_scholar.py

# Test basic module structure
python -c "
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from dotenv import load_dotenv
print('✅ All MCP dependencies available')
"
```

### Phase 3: Dependency Validation
```bash
# Test core functionality imports
python -c "
# Test MCP functionality
from mcp import ClientSession, StdioServerParameters
print('✅ MCP imports successful')

# Test OpenAI compatibility
from openai import AsyncOpenAI
print('✅ OpenAI import successful')

# Test environment configuration
from dotenv import load_dotenv
print('✅ dotenv import successful')

# Test HTTP libraries for external APIs
import requests
print('✅ requests available for external APIs')
"
```

### Phase 4: Basic Functionality Testing
```bash
# Run simplified test suite
python simple_test.py

# Test server initialization (dry run)
python -c "
import sys
sys.path.insert(0, 'src')
try:
    # Test pubmed server basic functionality
    import servers.pubmed_server
    print('✅ PubMed server module loads')
    
    # Test semantic scholar server
    import servers.semantic_scholar  
    print('✅ Semantic Scholar server module loads')
    
except Exception as e:
    print(f'❌ Server test failed: {e}')
"
```

### Phase 5: MCP Server Connectivity Test
```python
# Test MCP server initialization
import asyncio
import sys
sys.path.insert(0, 'src')

async def test_mcp_servers():
    try:
        # Test server configurations
        from mcp import StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        servers = {
            "pubmed": StdioServerParameters(
                command="python",
                args=["src/servers/pubmed_server.py"]
            ),
            "semantic_scholar": StdioServerParameters(
                command="python", 
                args=["src/servers/semantic_scholar.py"]
            )
        }
        
        print("✅ Server configurations defined successfully")
        
        # Note: Full test requires actual server startup
        # This is a configuration validation step
        
    except Exception as e:
        print(f"❌ MCP configuration test failed: {e}")

# Run configuration test
asyncio.run(test_mcp_servers())
```

### Phase 6: API Integration Testing
```bash
# Test API connectivity
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

# Test OpenRouter configuration
api_key = os.getenv('OPENROUTER_API_KEY')
base_url = os.getenv('OPENROUTER_BASE_URL')
model = os.getenv('OPENROUTER_MODEL')

if api_key and base_url and model:
    print('✅ OpenRouter configuration complete')
else:
    print('❌ Missing OpenRouter configuration')

# Test basic HTTP connectivity
import requests
try:
    response = requests.get('https://eutils.ncbi.nlm.nih.gov', timeout=5)
    print('✅ NCBI E-utilities accessible')
except Exception as e:
    print(f'❌ NCBI connectivity test failed: {e}')
"
```

### Phase 7: Prompt Validation
```python
# Test prompt loading and processing
def test_prompts():
    import os
    
    prompt_dir = 'prompts'
    example_dir = 'examples'
    
    # Test prompt file existence and readability
    for directory in [prompt_dir, example_dir]:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith(('.txt', '.md', '.json')):
                    try:
                        with open(os.path.join(directory, file), 'r') as f:
                            content = f.read()
                        print(f'✅ {directory}/{file}: {len(content)} characters')
                    except Exception as e:
                        print(f'❌ Failed to read {directory}/{file}: {e}')
    
    # Test output directory creation
    os.makedirs('research_outputs', exist_ok=True)
    print('✅ Output directory ready')

test_prompts()
```

### Phase 8: Test Suite Execution
```bash
# Run unit tests (excluding problematic tests)
pytest tests/unit -v --tb=short

# Run integration tests
pytest tests/integration -v --tb=short --cov=src

# Run security tests
pytest tests/security -v --tb=short

# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

## Common Issues and Solutions

### 1. Import Errors
**Problem**: `ModuleNotFoundError` for MCP or OpenAI dependencies
**Solution**: 
```bash
pip install mcp>=1.0.0 openai>=1.50.0 python-dotenv>=1.0.0 httpx>=0.27.0
```

### 2. Missing Environment Configuration
**Problem**: API keys missing
**Solution**:
```bash
# Copy example and fill in credentials
cp .env.example .env
# Edit .env with actual API keys
```

### 3. Network Connectivity Issues
**Problem**: External API timeouts
**Solution**:
- Check internet connectivity
- Verify API endpoints are accessible
- Consider adding timeout configurations

### 4. Server Startup Failures
**Problem**: MCP servers fail to initialize
**Solution**:
- Verify Node.js is installed (for filesystem server)
- Check Python path includes src directory
- Ensure server scripts have execute permissions

### 5. Performance Test Dependencies
**Problem**: Missing performance testing dependencies
**Solution**:
```bash
pip install pytest-benchmark psutil
```

## Success Criteria

A MCP research agent is considered validated when:

✅ **All syntax checks pass**: No compilation errors  
✅ **Core modules import successfully**: Agent and all servers load  
✅ **MCP configurations defined**: Server parameters properly set  
✅ **API configuration complete**: Necessary credentials available  
✅ **Basic functionality tested**: Simple operations succeed  
✅ **Test suite passes**: Unit and integration tests successful  
✅ **Documentation complete**: README and examples accessible  

## Usage Examples

### Quick Validation
```bash
# Basic validation
python simple_test.py

# Syntax check
python -m py_compile src/agent.py src/servers/*.py

# Import verification
python -c "import sys; sys.path.insert(0, 'src'); import agent; print('✅ Ready')"
```

### Comprehensive Validation
```bash
# Full validation suite
./validate_agent.sh

# This would run all phases:
# 1. Environment check
# 2. Syntax validation  
# 3. Dependency verification
# 4. MCP configuration test
# 5. API integration test
# 6. Prompt validation
# 7. Test suite execution
```

## Best Practices

1. **Environment Isolation**: Use virtual environments for testing
2. **Incremental Testing**: Test components individually before integration
3. **Error Handling**: Validate error handling and recovery mechanisms
4. **Configuration Management**: Secure storage of API credentials
5. **Documentation**: Keep validation procedures updated with code changes
6. **Performance Monitoring**: Include performance benchmarks for critical operations
7. **Network Testing**: Test both online and offline scenarios where applicable