"""
Performance benchmarking tests for the biomedical research agent
"""
import pytest
import asyncio
import time
import json
import os
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from unittest.mock import Mock, AsyncMock, patch
import sys
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent


class PerformanceBenchmark:
    """Performance benchmarking utility class"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.psutil_available = PSUTIL_AVAILABLE

    def start(self):
        """Start benchmarking"""
        self.start_time = time.time()
        self.memory_usage = []
        self.cpu_usage = []

    def end(self):
        """End benchmarking"""
        self.end_time = time.time()

    def record_metrics(self):
        """Record current resource usage"""
        if not self.psutil_available:
            return
        
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())

    def get_results(self) -> Dict[str, Any]:
        """Get benchmark results"""
        if self.start_time is None or self.end_time is None:
            return {}

        results = {
            "execution_time": self.end_time - self.start_time,
            "psutil_available": self.psutil_available,
            "memory_samples": len(self.memory_usage),
            "cpu_samples": len(self.cpu_usage)
        }

        if self.psutil_available and self.memory_usage:
            results.update({
                "avg_memory_usage": sum(self.memory_usage) / len(self.memory_usage),
                "max_memory_usage": max(self.memory_usage),
                "avg_cpu_usage": sum(self.cpu_usage) / len(self.cpu_usage),
                "max_cpu_usage": max(self.cpu_usage)
            })

        return results


class TestAgentPerformance:
    """Performance tests for the research agent"""

    @pytest.mark.performance
    async def test_agent_startup_performance(self):
        """Test agent startup performance"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup minimal response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Test response"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock sessions
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test startup performance
            await run_research_agent("test prompt")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Assert startup is fast (< 2 seconds)
            assert results["execution_time"] < 2.0
            if results["psutil_available"]:
                assert results["max_memory_usage"] < 100  # Less than 100MB

    @pytest.mark.performance
    async def test_concurrent_request_performance(self):
        """Test performance with concurrent requests"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track request count
            request_count = 0
            
            def mock_response_generator():
                nonlocal request_count
                request_count += 1
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Response {request_count}"
                mock_response.choices[0].message.tool_calls = None if request_count > 3 else [Mock(
                    id=f"tool_{request_count}",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "test", "limit": 5}'
                    )
                )]
                return mock_response
            
            mock_client.chat.completions.create.side_effect = mock_response_generator
            
            # Setup mock servers
            mock_pubmed_session = Mock()
            mock_fs_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_fs_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content="Mock result"))
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Test concurrent performance
            prompt = "Execute multiple concurrent searches"
            await run_research_agent(prompt)
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Should complete within 10 seconds for 5 iterations
            assert results["execution_time"] < 10.0
            assert request_count == 5  # Should have executed 5 iterations
            if results["psutil_available"]:
                assert results["max_memory_usage"] < 100  # Less than 100MB

    @pytest.mark.performance
    async def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Mock response for large dataset
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Processing large dataset"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="large_search",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "large dataset test", "limit": 50}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with large dataset response
            mock_pubmed_session = Mock()
            mock_fs_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_fs_session.initialize = AsyncMock()
            
            # Generate large mock dataset
            large_dataset = {"query": "large dataset test", "count": 50, "papers": []}
            for i in range(50):
                large_dataset["papers"].append({
                    "pubmed_id": f"{i+1:07d}",
                    "title": f"Large Paper {i+1}",
                    "authors": [f"Author {j+1}" for j in range(10)],
                    "abstract": "This is a large abstract with substantial content for testing performance with big datasets.",
                    "journal": "Journal of Large Studies",
                    "publication_date": f"202{i}-01-01"
                })
            
            mock_pubmed_session.call_tool = AsyncMock(
                return_value=Mock(content=json.dumps(large_dataset))
            )
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Test large dataset performance
            await run_research_agent("Process large dataset")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Should handle large datasets within reasonable time
            assert results["execution_time"] < 15.0
            if results["psutil_available"]:
                assert results["max_memory_usage"] < 200  # Less than 200MB

    @pytest.mark.performance
    async def test_memory_usage_stability(self):
        """Test memory usage stability over multiple runs"""
        memory_samples = []
        
        for i in range(5):
            benchmark = PerformanceBenchmark()
            benchmark.start()
            
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_makedirs:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Memory test {i+1}"
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                await run_research_agent(f"memory test {i+1}")
                
                benchmark.end()
                results = benchmark.get_results()
                memory_samples.append(results)
            
            # Clean up between runs
            await asyncio.sleep(0.1)
        
        # Check memory stability (no more than 20% variation between runs)
        avg_memory = sum(memory_samples) / len(memory_samples)
        max_variation = max(abs(m - avg_memory) for m in memory_samples)
        variation_percentage = (max_variation / avg_memory) * 100 if avg_memory > 0 else 0
        
        assert variation_percentage < 20.0, f"Memory usage too variable: {variation_percentage}%"

    @pytest.mark.performance
    async def test_cpu_usage_efficiency(self):
        """Test CPU usage efficiency"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "CPU efficiency test"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await run_research_agent("CPU efficiency test")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # CPU usage should be reasonable
            if results["psutil_available"]:
                assert results["avg_cpu_usage"] < 50.0  # Less than 50% average CPU
                assert results["max_cpu_usage"] < 80.0   # Less than 80% peak CPU


class TestServerPerformance:
    """Performance tests for MCP servers"""

    @pytest.mark.performance
    async def test_pubmed_server_performance(self):
        """Test PubMed server performance"""
        from fixtures.mcp_mocks import MockPubmedServer
        
        server = MockPubmedServer()
        await server.initialize()
        
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        # Test multiple searches
        for i in range(10):
            await server.call_tool("search_pubmed", {
                "query": f"performance_test_{i}",
                "year": "2020-2024",
                "limit": 10
            })
        
        benchmark.end()
        results = benchmark.get_results()
        
        # Should handle 10 searches quickly
        assert results["execution_time"] < 5.0
        assert results["max_memory_usage"] < 50  # Less than 50MB

    @pytest.mark.performance
    async def test_semantic_scholar_server_performance(self):
        """Test Semantic Scholar server performance"""
        from fixtures.mcp_mocks import MockSemanticScholarServer
        
        server = MockSemanticScholarServer()
        await server.initialize()
        
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        # Test multiple searches
        for i in range(8):
            await server.call_tool("search_semantic_scholar", {
                "query": f"performance_test_{i}",
                "year": "2020-2024",
                "limit": 8
            })
        
        benchmark.end()
        results = benchmark.get_results()
        
        # Should handle 8 searches quickly
        assert results["execution_time"] < 4.0
        assert results["max_memory_usage"] < 40  # Less than 40MB

    @pytest.mark.performance
    async def test_filesystem_server_performance(self):
        """Test filesystem server performance"""
        from fixtures.mcp_mocks import MockFilesystemServer
        
        server = MockFilesystemServer()
        await server.initialize()
        
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        # Test multiple file operations
        for i in range(20):
            await server.call_tool("write_file", {
                "path": f"/tmp/test_{i}.txt",
                "content": f"Test content {i}" * 100  # 100x repeated content
            })
        
        benchmark.end()
        results = benchmark.get_results()
        
        # Should handle 20 file operations quickly
        assert results["execution_time"] < 3.0
        assert results["max_memory_usage"] < 30  # Less than 30MB


class TestLoadPerformance:
    """Load testing for the research agent"""

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_multiple_concurrent_agents(self):
        """Test performance with multiple concurrent agents"""
        import concurrent.futures
        
        def run_agent_task(task_id):
            async def run_agent():
                with patch('agent.client') as mock_client, \
                     patch('agent.stdio_client') as mock_stdio, \
                     patch('agent.ClientSession') as mock_session_class, \
                     patch('agent.os.makedirs') as mock_makedirs:
                    
                    mock_response = Mock()
                    mock_response.choices = [Mock()]
                    mock_response.choices[0].message = Mock()
                    mock_response.choices[0].message.content = f"Concurrent task {task_id}"
                    mock_response.choices[0].message.tool_calls = None
                    mock_client.chat.completions.create.return_value = mock_response
                    
                    mock_session = Mock()
                    mock_session.initialize = AsyncMock()
                    mock_session_class.return_value = mock_session
                    
                    await run_research_agent(f"concurrent test {task_id}")
                    return f"Task {task_id} completed"
            
            return asyncio.run(run_agent())
        
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        # Test 5 concurrent agents
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, run_agent_task, i) for i in range(5)]
            results = await asyncio.gather(*tasks)
        
        benchmark.end()
        performance_results = benchmark.get_results()
        
        # All tasks should complete within reasonable time
        assert performance_results["execution_time"] < 15.0
        assert len(results) == 5
        assert all("completed" in result for result in results)

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_long_running_session_performance(self):
        """Test performance of long-running sessions"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Generate multiple responses for long session
            responses = []
            for i in range(10):  # 10 iterations
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Long session step {i+1}"
                mock_response.choices[0].message.tool_calls = None if i >= 8 else [Mock(
                    id=f"tool_{i}",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "long session test", "limit": 3}'
                    )
                )]
                responses.append(mock_response)
            
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers
            mock_pubmed_session = Mock()
            mock_fs_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_fs_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content="Mock result"))
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Test long session performance
            await run_research_agent("Long running session test")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Should handle 10 iterations within reasonable time
            assert results["execution_time"] < 30.0
            assert results["max_memory_usage"] < 150  # Less than 150MB


class TestPerformanceMetrics:
    """Performance metrics collection and validation"""

    @pytest.mark.performance
    async def test_response_time_metrics(self):
        """Test response time metrics collection"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Response time test"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await run_research_agent("response time test")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Validate response time metrics
            assert "execution_time" in results
            assert results["execution_time"] > 0
            assert isinstance(results["execution_time"], (int, float))

    @pytest.mark.performance
    async def test_memory_usage_metrics(self):
        """Test memory usage metrics collection"""
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Memory usage test"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await run_research_agent("memory usage test")
            
            benchmark.end()
            results = benchmark.get_results()
            
            # Validate memory usage metrics
            assert "avg_memory_usage" in results
            assert "max_memory_usage" in results
            assert results["avg_memory_usage"] >= 0
            assert results["max_memory_usage"] >= 0

    @pytest.mark.performance
    async def test_performance_regression_detection(self):
        """Test performance regression detection"""
        # Baseline performance (from previous runs)
        baseline_metrics = {
            "execution_time": 2.5,
            "max_memory_usage": 80.0,
            "avg_cpu_usage": 30.0
        }
        
        # Current performance
        benchmark = PerformanceBenchmark()
        benchmark.start()
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Regression test"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await run_research_agent("regression test")
            
            benchmark.end()
            current_metrics = benchmark.get_results()
        
        # Check for regressions (allow 50% increase)
        time_regression = (current_metrics["execution_time"] - baseline_metrics["execution_time"]) / baseline_metrics["execution_time"]
        memory_regression = (current_metrics["max_memory_usage"] - baseline_metrics["max_memory_usage"]) / baseline_metrics["max_memory_usage"]
        
        # Assert no significant regressions
        assert time_regression < 0.5, f"Time regression detected: {time_regression*100:.1f}%"
        assert memory_regression < 0.5, f"Memory regression detected: {memory_regression*100:.1f}%"