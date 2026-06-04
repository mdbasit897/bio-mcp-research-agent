"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
import tempfile
import shutil
import os
from unittest.mock import Mock, AsyncMock, patch
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('agent.client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_stdio_client():
    """Mock stdio client for testing."""
    with patch('agent.stdio_client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_client_session():
    """Mock MCP client session for testing."""
    with patch('agent.ClientSession') as mock_session:
        yield mock_session


@pytest.fixture
def mock_mcp_servers():
    """Mock MCP servers for testing."""
    servers = {
        'pubmed': Mock(),
        'semantic_scholar': Mock(),
        'filesystem': Mock()
    }
    for server in servers.values():
        server.initialize = AsyncMock()
        server.list_tools = Mock()
        server.call_tool = AsyncMock()
    yield servers


@pytest.fixture
def sample_research_prompt():
    """Sample research prompt for testing."""
    return """
    Act as an expert biomedical AI researcher.
    1. Use `search_pubmed` to find 5 recent papers on "non-invasive glucose monitoring"
    2. Fetch their abstracts using `fetch_pubmed_abstracts`
    3. Save analysis to `research_outputs/test_analysis.md`
    """


@pytest.fixture
def sample_pubmed_response():
    """Sample PubMed API response for testing."""
    return {
        "query": "non-invasive glucose monitoring",
        "count": 5,
        "papers": [
            {
                "pubmed_id": "12345678",
                "title": "Deep Learning for Non-invasive Glucose Monitoring",
                "authors": ["Smith, J.", "Johnson, A."],
                "journal": "Journal of Medical AI",
                "publication_date": "2024-01-15",
                "abstract": "This paper presents a novel deep learning approach..."
            }
        ]
    }


@pytest.fixture
def sample_semantic_scholar_response():
    """Sample Semantic Scholar API response for testing."""
    return {
        "query": "machine learning healthcare",
        "count": 3,
        "papers": [
            {
                "paper_id": "semantic_12345",
                "title": "AI Applications in Healthcare",
                "authors": [{"name": "Dr. Alice Smith", "authorId": "author_123"}],
                "year": 2024,
                "citationCount": 45,
                "abstract": "Comprehensive review of AI applications..."
            }
        ]
    }


@pytest.fixture
def benchmark_data():
    """Benchmark data for performance testing."""
    return {
        "execution_times": [1.2, 1.5, 1.3, 1.8, 1.4],
        "memory_usage": [45, 48, 46, 52, 47],
        "cpu_usage": [25, 30, 28, 35, 27]
    }


@pytest.fixture
def security_test_cases():
    """Security test cases for input validation."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "SELECT * FROM users"
        ],
        "xss_attacks": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src='x' onerror='alert(1)'>"
        ],
        "command_injection": [
            "test; rm -rf /",
            "test && cat /etc/passwd",
            "test || rm -rf /"
        ]
    }


@pytest.fixture
def test_metrics():
    """Test metrics for validation."""
    return {
        "code_coverage": {
            "target": 85,
            "unit": 90,
            "integration": 80,
            "e2e": 75,
            "security": 95
        },
        "performance": {
            "max_response_time": 5.0,
            "max_memory_usage": 100,
            "max_cpu_usage": 80,
            "min_throughput": 10
        },
        "quality": {
            "max_complexity": 10,
            "max_line_length": 127,
            "min_documentation": 80
        }
    }


@pytest.fixture
def pytest_plugins():
    """Pytest plugins configuration."""
    return [
        'pytest_cov',
        'pytest_asyncio',
        'pytest_mock',
        'pytest_benchmark',
        'pytest_html'
    ]


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests that test complete workflows"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests and benchmarks"
    )
    config.addinivalue_line(
        "markers", "security: Security and vulnerability tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "real_api: Tests that require real API access"
    )
    config.addinivalue_line(
        "markers", "skip_ci: Tests to skip in CI environment"
    )


# Performance monitoring fixtures
@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start(self):
            """Start monitoring."""
            import time
            self.start_time = time.time()
            self.metrics = {}
        
        def end(self):
            """End monitoring."""
            import time
            self.end_time = time.time()
        
        def get_duration(self):
            """Get total duration."""
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return PerformanceMonitor()


# Test data fixtures
@pytest.fixture
def test_dataset():
    """Test dataset for validation."""
    return {
        "papers": [
            {
                "id": "1",
                "title": "Paper 1",
                "authors": ["Author 1"],
                "year": 2023,
                "abstract": "Abstract 1"
            },
            {
                "id": "2",
                "title": "Paper 2",
                "authors": ["Author 2"],
                "year": 2024,
                "abstract": "Abstract 2"
            }
        ],
        "queries": [
            "machine learning healthcare",
            "non-invasive glucose monitoring",
            "AI biomedical applications"
        ]
    }


# Coverage configuration
@pytest.fixture
def coverage_config():
    """Coverage configuration."""
    return {
        "source": "src",
        "omit": [
            "*/tests/*",
            "*/test_*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/env/*"
        ],
        "report": {
            "show_missing": True,
            "precision": 2,
            "skip_covered": False
        }
    }


# Mock fixtures for common scenarios
@pytest.fixture
def successful_response():
    """Mock successful response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Success"
    mock_response.choices[0].message.tool_calls = None
    return mock_response


@pytest.fixture
def error_response():
    """Mock error response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Error occurred"
    mock_response.choices[0].message.tool_calls = None
    return mock_response


@pytest.fixture
def tool_call_response():
    """Mock tool call response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "I'll search for papers"
    mock_response.choices[0].message.tool_calls = [Mock(
        id="test_tool",
        function=Mock(
            name="search_pubmed",
            arguments='{"query": "test", "limit": 5}'
        )
    )]
    return mock_response