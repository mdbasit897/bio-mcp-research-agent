"""
Integration tests for MCP server interactions
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fixtures.mcp_mocks import (
    MockPubmedServer,
    MockSemanticScholarServer,
    MockFilesystemServer,
    MockMCPClient
)
from agent import run_research_agent


class TestMCPServerIntegration:
    """Integration tests for MCP server interactions"""

    @pytest.mark.integration
    async def test_pubmed_server_initialization(self):
        """Test PubMed server initialization and tool registration"""
        server = MockPubmedServer()
        
        # Test server initialization
        await server.initialize()
        assert server.initialized is True
        
        # Test tool listing
        tools = await server.list_tools()
        assert len(tools.tools) == 2  # search_pubmed and fetch_pubmed_abstracts
        
        tool_names = [tool.name for tool in tools.tools]
        assert "search_pubmed" in tool_names
        assert "fetch_pubmed_abstracts" in tool_names

    @pytest.mark.integration
    async def test_pubmed_search_execution(self):
        """Test PubMed search tool execution"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Execute search
        result = await server.call_tool("search_pubmed", {
            "query": "non-invasive glucose monitoring",
            "year": "2020-2024",
            "limit": 5
        })
        
        # Validate result
        assert result.content["query"] == "non-invasive glucose monitoring"
        assert result.content["count"] == 5
        assert len(result.content["papers"]) == 5
        
        # Validate paper structure
        paper = result.content["papers"][0]
        assert "pubmed_id" in paper
        assert "title" in paper
        assert "authors" in paper
        assert "journal" in paper
        assert "publication_date" in paper

    @pytest.mark.integration
    async def test_pubmed_abstract_fetching(self):
        """Test PubMed abstract fetching tool execution"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Execute abstract fetching
        result = await server.call_tool("fetch_pubmed_abstracts", {
            "pmids": ["1234567", "2345678", "3456789"]
        })
        
        # Validate result
        assert result.content["count"] == 3
        assert len(result.content["abstracts"]) == 3
        
        # Validate abstract structure
        abstract = result.content["abstracts"][0]
        assert "pubmed_id" in abstract
        assert "title" in abstract
        assert "abstract" in abstract
        assert "methods" in abstract
        assert "results" in abstract
        assert "conclusions" in abstract
        assert "limitations" in abstract
        assert "future_work" in abstract
        assert "mard_score" in abstract
        assert "sensitivity" in abstract
        assert "specificity" in abstract

    @pytest.mark.integration
    async def test_semantic_scholar_initialization(self):
        """Test Semantic Scholar server initialization"""
        server = MockSemanticScholarServer()
        await server.initialize()
        
        assert server.initialized is True
        
        # Test tool listing
        tools = await server.list_tools()
        assert len(tools.tools) == 1  # search_semantic_scholar
        assert tools.tools[0].name == "search_semantic_scholar"

    @pytest.mark.integration
    async def test_semantic_scholar_search_execution(self):
        """Test Semantic Scholar search tool execution"""
        server = MockSemanticScholarServer()
        await server.initialize()
        
        result = await server.call_tool("search_semantic_scholar", {
            "query": "machine learning healthcare",
            "year": "2020-2024",
            "limit": 3
        })
        
        # Validate result
        assert result.content["query"] == "machine learning healthcare"
        assert result.content["count"] == 3
        assert len(result.content["papers"]) == 3
        
        # Validate paper structure
        paper = result.content["papers"][0]
        assert "paper_id" in paper
        assert "title" in paper
        assert "authors" in paper
        assert "year" in paper
        assert "citationCount" in paper
        assert "abstract" in paper
        assert "fieldsOfStudy" in paper

    @pytest.mark.integration
    async def test_filesystem_server_initialization(self):
        """Test filesystem server initialization"""
        server = MockFilesystemServer()
        await server.initialize()
        
        assert server.initialized is True
        
        # Test tool listing
        tools = await server.list_tools()
        assert len(tools.tools) == 4  # read_file, write_file, list_directory, create_directory

    @pytest.mark.integration
    async def test_filesystem_operations(self):
        """Test filesystem tool operations"""
        server = MockFilesystemServer()
        await server.initialize()
        
        # Test file creation
        result = await server.call_tool("write_file", {
            "path": "/tmp/test_output.md",
            "content": "# Test Research Output\n\nThis is a test file."
        })
        assert result.content == "File /tmp/test_output.md created successfully"
        
        # Test file reading
        result = await server.call_tool("read_file", {
            "path": "/tmp/test_output.md"
        })
        assert result.content == "# Test Research Output\n\nThis is a test file."
        
        # Test directory creation
        result = await server.call_tool("create_directory", {
            "path": "/tmp/test_research"
        })
        assert result.content == "Directory /tmp/test_research created successfully"
        
        # Test directory listing
        result = await server.call_tool("list_directory", {
            "path": "/tmp"
        })
        assert result.content["count"] >= 1
        assert "/tmp/test_output.md" in result.content["files"]

    @pytest.mark.integration
    async def test_error_handling_invalid_tool_name(self):
        """Test error handling for invalid tool names"""
        server = MockPubmedServer()
        await server.initialize()
        
        with pytest.raises(ValueError, match="Tool not_found not found"):
            await server.call_tool("not_found", {})

    @pytest.mark.integration
    async def test_error_handling_invalid_parameters(self):
        """Test error handling for invalid parameters"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Test empty query
        result = await server.call_tool("search_pubmed", {
            "query": "",
            "year": "2020-2024",
            "limit": 5
        })
        assert "Error:" in result.content
        
        # Test invalid limit
        result = await server.call_tool("search_pubmed", {
            "query": "test",
            "year": "2020-2024",
            "limit": 0
        })
        assert "Error:" in result.content

    @pytest.mark.integration
    async def test_concurrent_tool_execution(self):
        """Test concurrent execution of multiple tools"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Execute multiple searches concurrently
        tasks = []
        for i in range(3):
            task = server.call_tool("search_pubmed", {
                "query": f"test_query_{i}",
                "year": "2020-2024",
                "limit": 2
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Validate all results
        for i, result in enumerate(results):
            assert result.content["query"] == f"test_query_{i}"
            assert result.content["count"] == 2
            assert len(result.content["papers"]) == 2

    @pytest.mark.integration
    async def test_tool_parameter_validation(self):
        """Test comprehensive parameter validation"""
        server = MockPubmedServer()
        await server.initialize()
        
        test_cases = [
            # Valid cases
            {
                "params": {"query": "valid", "year": "2020-2024", "limit": 5},
                "should_succeed": True
            },
            {
                "params": {"query": "valid", "year": "2020-2024", "limit": 10},
                "should_succeed": True
            },
            # Invalid cases
            {
                "params": {"query": "", "year": "2020-2024", "limit": 5},
                "should_succeed": False
            },
            {
                "params": {"query": "valid", "year": "2020-2024", "limit": 0},
                "should_succeed": False
            },
            {
                "params": {"query": "valid", "year": "2020-2024", "limit": 101},
                "should_succeed": False
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await server.call_tool("search_pubmed", test_case["params"])
                if test_case["should_succeed"]:
                    assert "Error:" not in result.content
                else:
                    assert "Error:" in result.content
            except Exception as e:
                if not test_case["should_succeed"]:
                    pass  # Expected failure
                else:
                    raise e


class TestMCPServerCommunication:
    """Test MCP server communication protocols"""

    @pytest.mark.integration
    async def test_server_initialization_sequence(self):
        """Test proper server initialization sequence"""
        servers = {
            "pubmed": MockPubmedServer(),
            "semantic_scholar": MockSemanticScholarServer(),
            "filesystem": MockFilesystemServer()
        }
        
        # Initialize all servers
        for name, server in servers.items():
            await server.initialize()
            assert server.initialized is True
        
        # Test tool availability
        for name, server in servers.items():
            tools = await server.list_tools()
            assert len(tools.tools) > 0

    @pytest.mark.integration
    async def test_cross_server_data_flow(self):
        """Test data flow between different servers"""
        pubmed_server = MockPubmedServer()
        fs_server = MockFilesystemServer()
        
        await pubmed_server.initialize()
        await fs_server.initialize()
        
        # Step 1: Search PubMed
        search_result = await pubmed_server.call_tool("search_pubmed", {
            "query": "glucose monitoring",
            "year": "2020-2024",
            "limit": 3
        })
        
        # Step 2: Save results to filesystem
        fs_result = await fs_server.call_tool("write_file", {
            "path": "/tmp/search_results.json",
            "content": json.dumps(search_result.content, indent=2)
        })
        
        # Step 3: Read back from filesystem
        read_result = await fs_server.call_tool("read_file", {
            "path": "/tmp/search_results.json"
        })
        
        # Validate data integrity
        assert fs_result.content == "File /tmp/search_results.json created successfully"
        data = json.loads(read_result.content)
        assert data["query"] == "glucose monitoring"
        assert data["count"] == 3

    @pytest.mark.integration
    async def test_server_error_propagation(self):
        """Test error propagation between servers"""
        pubmed_server = MockPubmedServer()
        await pubmed_server.initialize()
        
        # Test that errors are properly propagated
        with pytest.raises(ValueError, match="Tool not_found not found"):
            await pubmed_server.call_tool("not_found", {})


class TestMCPServerPerformance:
    """Test MCP server performance characteristics"""

    @pytest.mark.integration
    @pytest.mark.performance
    async def test_multiple_concurrent_requests(self):
        """Test handling of multiple concurrent requests"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Execute multiple concurrent searches
        num_requests = 10
        tasks = []
        
        for i in range(num_requests):
            task = server.call_tool("search_pubmed", {
                "query": f"concurrent_test_{i}",
                "year": "2020-2024",
                "limit": 2
            })
            tasks.append(task)
        
        # Measure execution time
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        
        # Validate results
        assert len(results) == num_requests
        for i, result in enumerate(results):
            assert result.content["query"] == f"concurrent_test_{i}"
            assert result.content["count"] == 2
        
        # Performance assertion (should complete within reasonable time)
        assert execution_time < 30  # Should complete within 30 seconds

    @pytest.mark.integration
    @pytest.mark.performance
    async def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Test with larger result set
        result = await server.call_tool("search_pubmed", {
            "query": "large_test",
            "year": "2020-2024",
            "limit": 20
        })
        
        # Validate large result handling
        assert result.content["count"] == 20
        assert len(result.content["papers"]) == 20
        
        # Validate memory efficiency by checking individual paper structure
        for paper in result.content["papers"]:
            assert "pubmed_id" in paper
            assert "title" in paper
            assert "authors" in paper

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_resource_cleanup(self):
        """Test proper resource cleanup"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Execute multiple operations
        for i in range(5):
            await server.call_tool("search_pubmed", {
                "query": f"cleanup_test_{i}",
                "year": "2020-2024",
                "limit": 3
            })
        
        # Server should still be functional after operations
        tools = await server.list_tools()
        assert len(tools.tools) == 2  # Should still have all tools


class TestMCPServerReliability:
    """Test MCP server reliability and resilience"""

    @pytest.mark.integration
    async def test_retry_mechanism(self):
        """Test retry mechanism for failed requests"""
        server = MockPubmedServer()
        await server.initialize()
        
        # Test that the server handles repeated requests correctly
        for i in range(3):
            result = await server.call_tool("search_pubmed", {
                "query": f"retry_test_{i}",
                "year": "2020-2024",
                "limit": 2
            })
            
            # Each request should succeed
            assert result.content["query"] == f"retry_test_{i}"
            assert result.content["count"] == 2

    @pytest.mark.integration
    async def test_consistent_responses(self):
        """Test that responses are consistent across multiple identical requests"""
        server = MockPubmedServer()
        await server.initialize()
        
        query = "consistency_test"
        results = []
        
        # Execute identical requests multiple times
        for i in range(5):
            result = await server.call_tool("search_pubmed", {
                "query": query,
                "year": "2020-2024",
                "limit": 3
            })
            results.append(result.content)
        
        # All responses should be identical in structure
        for i in range(1, len(results)):
            assert results[i]["query"] == results[0]["query"]
            assert results[i]["count"] == results[0]["count"]
            assert len(results[i]["papers"]) == len(results[0]["papers"])

    @pytest.mark.integration
    async def test_partial_failure_handling(self):
        """Test handling of partial failures in multi-step operations"""
        pubmed_server = MockPubmedServer()
        fs_server = MockFilesystemServer()
        
        await pubmed_server.initialize()
        await fs_server.initialize()
        
        # Step 1: Execute successful search
        search_result = await pubmed_server.call_tool("search_pubmed", {
            "query": "partial_failure_test",
            "year": "2020-2024",
            "limit": 2
        })
        
        # Step 2: Try to save (this should succeed)
        fs_result = await fs_server.call_tool("write_file", {
            "path": "/tmp/partial_test.json",
            "content": json.dumps(search_result.content)
        })
        
        # Validate that the partial operation succeeded
        assert fs_result.content == "File /tmp/partial_test.json created successfully"