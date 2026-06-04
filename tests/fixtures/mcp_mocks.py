"""
MCP server mock implementations for testing
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
import json


class MockResult:
    """Mock tool execution result"""

    def __init__(self, content: Any, content_type: str = "text"):
        self.content = content
        self.content_type = content_type


class MockToolList:
    """Mock tool list response"""

    def __init__(self, tools):
        self.tools = tools


class MockMCPClient:
    """Mock MCP client for testing server interactions"""
    
    def __init__(self):
        self.tools = {}
        self.initialized = False
    
    async def initialize(self):
        """Mock initialization"""
        self.initialized = True
    
    async def list_tools(self):
        """Mock list tools response"""
        return MockToolList(self.tools.values())
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MockResult:
        """Mock tool call"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        return await tool.execute(arguments)


class MockToolList:
    """Mock tool list response"""
    
    def __init__(self, tools):
        self.tools = tools


class MockResult:
    """Mock tool execution result"""
    
    def __init__(self, content: Any, content_type: str = "text"):
        self.content = content
        self.content_type = content_type


class MockPubmedServer(MockMCPClient):
    """Mock PubMed MCP server"""
    
    def __init__(self):
        super().__init__()
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup mock PubMed tools"""
        self.tools = {
            "search_pubmed": MockPubmedSearchTool(),
            "fetch_pubmed_abstracts": MockPubmedAbstractTool()
        }


class MockPubmedSearchTool:
    """Mock PubMed search tool"""
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock PubMed search"""
        query = arguments.get("query", "")
        year_range = arguments.get("year", "2020-2024")
        limit = arguments.get("limit", 10)
        
        # Validate arguments
        if not query or not query.strip():
            return MockResult("Error: Query cannot be empty", "text")
        
        if limit <= 0 or limit > 100:
            return MockResult("Error: Limit must be between 1 and 100", "text")
        
        # Generate mock results
        mock_results = []
        for i in range(min(limit, 10)):  # Limit to 10 mock results
            mock_results.append({
                "pubmed_id": f"{i+1:07d}",
                "title": f"Research on {query}: Paper {i+1}",
                "authors": [f"Author {j+1}" for j in range(3)],
                "journal": "Journal of Medical Research",
                "publication_date": f"202{i}-01-01",
                "doi": f"10.1000/paper{i+1}",
                "abstract": f"Abstract about {query} research methodology.",
                "keywords": [query, "machine learning", "biomedical"],
                "citation_count": 50 + i * 10
            })
        
        return MockResult({
            "query": query,
            "year_range": year_range,
            "count": len(mock_results),
            "papers": mock_results
        }, "json")


class MockPubmedAbstractTool:
    """Mock PubMed abstract fetch tool"""
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock PubMed abstract fetch"""
        pmids = arguments.get("pmids", [])
        
        if not pmids:
            return MockResult("Error: PMIDs list cannot be empty", "text")
        
        # Generate mock abstracts
        mock_abstracts = []
        for pmid in pmids:
            mock_abstracts.append({
                "pubmed_id": pmid,
                "title": f"Research Paper {pmid}",
                "abstract": f"Comprehensive abstract for paper {pmid}. This research investigates novel methodologies for biomedical data analysis.",
                "methods": "We employed deep learning models trained on multi-modal datasets.",
                "results": "Our model achieved significant improvements in predictive accuracy.",
                "conclusions": "The proposed method shows promise for clinical applications.",
                "limitations": "Limited sample size and need for validation.",
                "future_work": "Further validation studies and integration with clinical systems.",
                "mard_score": 8.5 + (hash(pmid) % 10) * 0.1,
                "sensitivity": 0.92 + (hash(pmid) % 8) * 0.01,
                "specificity": 0.94 + (hash(pmid) % 6) * 0.01
            })
        
        return MockResult({
            "count": len(mock_abstracts),
            "abstracts": mock_abstracts
        }, "json")


class MockSemanticScholarServer(MockMCPClient):
    """Mock Semantic Scholar MCP server"""
    
    def __init__(self):
        super().__init__()
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup mock Semantic Scholar tools"""
        self.tools = {
            "search_semantic_scholar": MockSemanticScholarSearchTool()
        }


class MockSemanticScholarSearchTool:
    """Mock Semantic Scholar search tool"""
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock Semantic Scholar search"""
        query = arguments.get("query", "")
        year = arguments.get("year", "2020-2024")
        limit = arguments.get("limit", 10)
        
        # Validate arguments
        if not query or not query.strip():
            return MockResult("Error: Query cannot be empty", "text")
        
        if limit <= 0 or limit > 50:
            return MockResult("Error: Limit must be between 1 and 50", "text")
        
        # Generate mock results
        mock_results = []
        for i in range(min(limit, 8)):  # Limit to 8 mock results
            mock_results.append({
                "paper_id": f"semantic_{uuid.uuid4()}",
                "title": f"AI-powered {query} research: Paper {i+1}",
                "authors": [
                    {"name": f"Author {j+1}", "authorId": f"author_{j+1}"} 
                    for j in range(3)
                ],
                "year": 2024 - i,
                "citationCount": 100 + i * 20,
                "influentialCitationCount": 50 + i * 10,
                "openAccessPdf": {
                    "url": f"https://arxiv.org/pdf/{i+1:04d}.1234.pdf"
                } if i % 2 == 0 else None,
                "venue": f"Conference on {query} Research",
                "abstract": f"Advanced research in {query} using artificial intelligence.",
                "fieldsOfStudy": ["Computer Science", "Medicine"],
                "publicationTypes": ["Journal Article"],
                "externalIds": {
                    "PubMed": f"{i+1:07d}",
                    "ArXiv": f"{i+1:04d}.1234"
                }
            })
        
        return MockResult({
            "query": query,
            "year_range": year,
            "count": len(mock_results),
            "papers": mock_results
        }, "json")


class MockFilesystemServer(MockMCPClient):
    """Mock Filesystem MCP server"""
    
    def __init__(self, temp_dir: str = "/tmp/test_fs"):
        super().__init__()
        self.temp_dir = temp_dir
        self.created_files = {}
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup mock filesystem tools"""
        self.tools = {
            "read_file": MockReadFileTool(self),
            "write_file": MockWriteFileTool(self),
            "list_directory": MockListDirectoryTool(self),
            "create_directory": MockCreateDirectoryTool(self)
        }


class MockReadFileTool:
    """Mock read file tool"""
    
    def __init__(self, server):
        self.server = server
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock file read"""
        file_path = arguments.get("path", "")
        
        if not file_path:
            return MockResult("Error: File path cannot be empty", "text")
        
        if file_path not in self.server.created_files:
            return MockResult(f"Error: File {file_path} not found", "text")
        
        return MockResult(self.server.created_files[file_path], "text")


class MockWriteFileTool:
    """Mock write file tool"""
    
    def __init__(self, server):
        self.server = server
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock file write"""
        file_path = arguments.get("path", "")
        content = arguments.get("content", "")
        
        if not file_path:
            return MockResult("Error: File path cannot be empty", "text")
        
        self.server.created_files[file_path] = content
        return MockResult(f"File {file_path} created successfully", "text")


class MockListDirectoryTool:
    """Mock list directory tool"""
    
    def __init__(self, server):
        self.server = server
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock directory listing"""
        dir_path = arguments.get("path", "")
        
        if not dir_path:
            return MockResult("Error: Directory path cannot be empty", "text")
        
        # Mock directory listing
        files = [f for f in self.server.created_files.keys() if f.startswith(dir_path)]
        directories = list(set(f.split('/')[1] for f in files if '/' in f))
        
        return MockResult({
            "path": dir_path,
            "files": files,
            "directories": directories,
            "count": len(files) + len(directories)
        }, "json")


class MockCreateDirectoryTool:
    """Mock create directory tool"""
    
    def __init__(self, server):
        self.server = server
    
    async def execute(self, arguments: Dict[str, Any]) -> MockResult:
        """Execute mock directory creation"""
        dir_path = arguments.get("path", "")
        
        if not dir_path:
            return MockResult("Error: Directory path cannot be empty", "text")
        
        # Mock directory creation
        if dir_path not in self.server.created_files:
            self.server.created_files[f"{dir_path}/"] = "directory"
        
        return MockResult(f"Directory {dir_path} created successfully", "text")


# UUID import needed for mock data
import uuid


@pytest.fixture
def mock_pubmed_server():
    """Fixture for mock PubMed server"""
    return MockPubmedServer()


@pytest.fixture
def mock_semantic_scholar_server():
    """Fixture for mock Semantic Scholar server"""
    return MockSemanticScholarServer()


@pytest.fixture
def mock_filesystem_server():
    """Fixture for mock filesystem server"""
    return MockFilesystemServer()


@pytest.fixture
def mock_mcp_clients():
    """Fixture for all mock MCP clients"""
    return {
        "pubmed": MockPubmedServer(),
        "semantic_scholar": MockSemanticScholarServer(),
        "filesystem": MockFilesystemServer()
    }


@pytest.fixture
async def initialized_mcp_servers(mock_mcp_clients):
    """Fixture for initialized MCP servers"""
    servers = {}
    for name, server in mock_mcp_clients.items():
        await server.initialize()
        servers[name] = server
    return servers


# Mock response patterns for different scenarios
class MockResponsePatterns:
    """Mock response patterns for testing various scenarios"""
    
    @staticmethod
    def success_response(data: Any) -> Dict[str, Any]:
        """Generate mock success response"""
        return {
            "status": "success",
            "data": data,
            "timestamp": asyncio.get_event_loop().time(),
            "request_id": str(uuid.uuid4())
        }
    
    @staticmethod
    def error_response(message: str, error_type: str = "validation") -> Dict[str, Any]:
        """Generate mock error response"""
        return {
            "status": "error",
            "message": message,
            "error_type": error_type,
            "timestamp": asyncio.get_event_loop().time(),
            "request_id": str(uuid.uuid4())
        }
    
    @staticmethod
    def rate_limited_response() -> Dict[str, Any]:
        """Generate mock rate limited response"""
        return {
            "status": "rate_limited",
            "message": "API rate limit exceeded",
            "retry_after": 60,
            "timestamp": asyncio.get_event_loop().time(),
            "request_id": str(uuid.uuid4())
        }


# Test scenario builders
class TestScenarioBuilder:
    """Builder class for creating test scenarios"""
    
    def __init__(self):
        self.scenarios = []
    
    def add_pubmed_search_scenario(self, query: str, expected_count: int = 5):
        """Add PubMed search scenario"""
        scenario = {
            "name": f"PubMed Search: {query}",
            "type": "pubmed_search",
            "query": query,
            "expected_count": expected_count,
            "expected_status": "success"
        }
        self.scenarios.append(scenario)
        return self
    
    def add_semantic_search_scenario(self, query: str, expected_count: int = 5):
        """Add Semantic Scholar search scenario"""
        scenario = {
            "name": f"Semantic Scholar Search: {query}",
            "type": "semantic_search",
            "query": query,
            "expected_count": expected_count,
            "expected_status": "success"
        }
        self.scenarios.append(scenario)
        return self
    
    def add_file_write_scenario(self, file_path: str, content: str):
        """Add file write scenario"""
        scenario = {
            "name": f"File Write: {file_path}",
            "type": "file_write",
            "file_path": file_path,
            "content": content,
            "expected_status": "success"
        }
        self.scenarios.append(scenario)
        return self
    
    def add_error_scenario(self, scenario_type: str, error_message: str):
        """Add error scenario"""
        scenario = {
            "name": f"Error: {scenario_type}",
            "type": "error",
            "error_type": scenario_type,
            "error_message": error_message,
            "expected_status": "error"
        }
        self.scenarios.append(scenario)
        return self
    
    def build(self) -> List[Dict[str, Any]]:
        """Build all scenarios"""
        return self.scenarios


@pytest.fixture
def test_scenario_builder():
    """Fixture for test scenario builder"""
    return TestScenarioBuilder()