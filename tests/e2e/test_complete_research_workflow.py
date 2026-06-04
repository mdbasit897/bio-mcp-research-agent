"""
End-to-end tests for complete research workflows
"""
import pytest
import asyncio
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent
from fixtures.mcp_mocks import MockPubmedServer, MockSemanticScholarServer, MockFilesystemServer


class TestCompleteResearchWorkflow:
    """End-to-end tests for complete research workflows"""

    @pytest.mark.e2e
    async def test_glucose_monitoring_research_workflow(self):
        """Test complete glucose monitoring research workflow"""
        # Define comprehensive research prompt
        prompt = """
        Act as an expert biomedical AI researcher specializing in non-invasive glucose monitoring.
        
        Execute the following systematic review:
        1. Use `search_pubmed` to find 8 recent papers (2020-2024) on "non-invasive glucose monitoring PPG machine learning"
        2. Fetch their abstracts using `fetch_pubmed_abstracts`
        3. Use the `filesystem` tool to save a comprehensive analysis to `research_outputs/glucose_monitoring_analysis.md` including:
           - MARD scores and accuracy metrics
           - Methodological approaches used
           - Dataset sizes and demographics
           - Key limitations identified
           - Clinical validation status
        4. Generate a 500-word executive summary highlighting the top 3 breakthroughs and 2 major challenges
        5. Identify the most promising approach for PhD research and explain why
        """
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track workflow execution
            workflow_steps = []
            
            def create_mock_response(step_name):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                
                if step_name == "initial":
                    mock_response.choices[0].message.content = "I'll start by searching PubMed for recent papers on non-invasive glucose monitoring"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="search_tool",
                        function=Mock(
                            name="search_pubmed",
                            arguments='{"query": "non-invasive glucose monitoring PPG machine learning", "limit": 8}'
                        )
                    )]
                elif step_name == "abstracts":
                    mock_response.choices[0].message.content = "Now I'll fetch the abstracts for these papers"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="abstract_tool",
                        function=Mock(
                            name="fetch_pubmed_abstracts",
                            arguments='{"pmids": ["1234567", "2345678", "3456789", "4567890", "5678901", "6789012", "7890123", "8901234"]}'
                        )
                    )]
                elif step_name == "analysis":
                    mock_response.choices[0].message.content = "I'll now save the comprehensive analysis"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="file_tool",
                        function=Mock(
                            name="write_file",
                            arguments='{"path": "research_outputs/glucose_monitoring_analysis.md", "content": "# Comprehensive Analysis\\n\\n## Executive Summary\\n..."}'
                        )
                    )]
                else:
                    mock_response.choices[0].message.content = "Research workflow completed successfully"
                    mock_response.choices[0].message.tool_calls = None
                
                return mock_response
            
            # Mock multiple responses for the workflow
            responses = [
                create_mock_response("initial"),
                create_mock_response("abstracts"),
                create_mock_response("analysis"),
                create_mock_response("final")
            ]
            
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_fs_session = MockFilesystemServer()
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock server responses
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({
                        "query": args.get("query", ""),
                        "count": args.get("limit", 5),
                        "papers": [
                            {
                                "pubmed_id": "1234567",
                                "title": "Deep Learning for Non-invasive Glucose Monitoring",
                                "authors": ["Author 1", "Author 2", "Author 3"],
                                "journal": "Journal of Medical Informatics",
                                "publication_date": "2024-01-15",
                                "abstract": "This paper presents a novel deep learning approach for non-invasive glucose monitoring using photoplethysmography signals.",
                                "methods": "CNN + LSTM architecture trained on multi-modal datasets",
                                "results": "Achieved 95.2% accuracy with MARD of 8.7 mg/dL",
                                "limitations": ["Single ethnicity cohort", "Limited device validation"],
                                "mard_score": 8.7,
                                "sensitivity": 0.92,
                                "specificity": 0.94
                            }
                        ]
                    })
                )
            )
            
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File created successfully"))
            
            # Execute workflow
            await run_research_agent(prompt)
            
            # Verify workflow completion
            assert mock_client.chat.completions.create.call_count == 4
            mock_pubmed_session.call_tool.assert_called()
            mock_fs_session.call_tool.assert_called()

    @pytest.mark.e2e
    async def test_multi_database_research_workflow(self):
        """Test research workflow using multiple databases"""
        prompt = """
        Act as an expert oncology AI researcher.
        
        Conduct a comprehensive analysis of AI in cancer diagnosis:
        1. Use `search_pubmed` to find 6 papers (2020-2024) on "deep learning cancer diagnosis radiomics"
        2. Use `search_semantic_scholar` to find 4 papers on "AI cancer prognosis biomarkers"
        3. Fetch abstracts from both sources
        4. Use the `filesystem` tool to create a comparative analysis in `research_outputs/cancer_ai_comparison.md`
        5. Generate insights on current trends, gaps, and future directions
        """
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track workflow steps
            steps = []
            
            def create_workflow_response(step):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                
                if step == 0:  # Initial search
                    mock_response.choices[0].message.content = "I'll search both PubMed and Semantic Scholar for cancer research"
                    mock_response.choices[0].message.tool_calls = [
                        Mock(
                            id="pubmed_search",
                            function=Mock(
                                name="search_pubmed",
                                arguments='{"query": "deep learning cancer diagnosis radiomics", "limit": 6}'
                            )
                        ),
                        Mock(
                            id="ss_search",
                            function=Mock(
                                name="search_semantic_scholar",
                                arguments='{"query": "AI cancer prognosis biomarkers", "limit": 4}'
                            )
                        )
                    ]
                elif step == 1:  # Abstract fetching
                    mock_response.choices[0].message.content = "Now I'll fetch abstracts from both sources"
                    mock_response.choices[0].message.tool_calls = [
                        Mock(
                            id="pubmed_abstracts",
                            function=Mock(
                                name="fetch_pubmed_abstracts",
                                arguments='{"pmids": ["1234567", "2345678", "3456789", "4567890", "5678901", "6789012"]}'
                            )
                        ),
                        Mock(
                            id="ss_abstracts",
                            function=Mock(
                                name="fetch_pubmed_abstracts",
                                arguments='{"pmids": ["7890123", "8901234", "9012345", "0123456"]}'
                            )
                        )
                    ]
                elif step == 2:  # File saving
                    mock_response.choices[0].message.content = "I'll save the comparative analysis"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="save_file",
                        function=Mock(
                            name="write_file",
                            arguments='{"path": "research_outputs/cancer_ai_comparison.md", "content": "# Cancer AI Analysis\\n..."}'
                        )
                    )]
                else:  # Final response
                    mock_response.choices[0].message.content = "Multi-database research completed successfully"
                    mock_response.choices[0].message.tool_calls = None
                
                return mock_response
            
            # Create sequence of responses
            responses = [create_workflow_response(i) for i in range(4)]
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_ss_session = MockSemanticScholarServer()
            mock_fs_session = MockFilesystemServer()
            
            call_log = []
            
            async def mock_session_init(*args, **kwargs):
                call_log.append(str(args))
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "semantic_scholar" in str(args):
                    return mock_ss_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_ss_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock server responses
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({"query": args.get("query", ""), "count": args.get("limit", 5)})
                )
            )
            mock_ss_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({"query": args.get("query", ""), "count": args.get("limit", 5)})
                )
            )
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            # Execute workflow
            await run_research_agent(prompt)
            
            # Verify workflow execution
            assert mock_client.chat.completions.create.call_count == 4
            assert len(call_log) >= 4  # Should have initialized multiple servers
            
            # Verify all servers were used
            pubmed_calls = [call for call in call_log if "pubmed" in call]
            ss_calls = [call for call in call_log if "semantic_scholar" in call]
            fs_calls = [call for call in call_log if "filesystem" in call]
            
            assert len(pubmed_calls) > 0
            assert len(ss_calls) > 0
            assert len(fs_calls) > 0

    @pytest.mark.e2e
    async def test_reproducible_research_workflow(self):
        """Test research workflow with reproducible results"""
        prompt = """
        Act as an expert researcher focused on reproducible science.
        
        Execute a reproducible research workflow:
        1. Use `search_pubmed` to find 5 papers on "reproducible machine learning biomedical"
        2. Fetch abstracts using `fetch_pubmed_abstracts`
        3. Use `search_semantic_scholar` to find additional papers on "reproducible research healthcare"
        4. Save results to `research_outputs/reproducible_research_analysis.md`
        5. Include methodology details and reproducibility scores in the analysis
        """
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track execution for reproducibility
            execution_log = []
            
            def create_reproducible_response(step):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                
                execution_log.append(f"Step {step + 1}")
                
                if step < 3:  # Tool calls
                    tool_calls = []
                    if step == 0:
                        tool_calls = [Mock(
                            id="pubmed_search",
                            function=Mock(
                                name="search_pubmed",
                                arguments='{"query": "reproducible machine learning biomedical", "limit": 5}'
                            )
                        )]
                    elif step == 1:
                        tool_calls = [Mock(
                            id="abstract_fetch",
                            function=Mock(
                                name="fetch_pubmed_abstracts",
                                arguments='{"pmids": ["1234567", "2345678", "3456789", "4567890", "5678901"]}'
                            )
                        )]
                    elif step == 2:
                        tool_calls = [
                            Mock(
                                id="ss_search",
                                function=Mock(
                                    name="search_semantic_scholar",
                                    arguments='{"query": "reproducible research healthcare", "limit": 5}'
                                )
                            ),
                            Mock(
                                id="save_file",
                                function=Mock(
                                    name="write_file",
                                    arguments='{"path": "research_outputs/reproducible_research_analysis.md", "content": "# Reproducible Research Analysis\\n..."}'
                                )
                            )
                        ]
                    
                    mock_response.choices[0].message.content = f"Executing step {step + 1}"
                    mock_response.choices[0].message.tool_calls = tool_calls
                else:  # Final response
                    mock_response.choices[0].message.content = "Reproducible research workflow completed"
                    mock_response.choices[0].message.tool_calls = None
                
                return mock_response
            
            responses = [create_reproducible_response(i) for i in range(4)]
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_ss_session = MockSemanticScholarServer()
            mock_fs_session = MockFilesystemServer()
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "semantic_scholar" in str(args):
                    return mock_ss_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_ss_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock consistent responses
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({
                        "query": args.get("query", ""),
                        "count": args.get("limit", 5),
                        "papers": []
                    })
                )
            )
            mock_ss_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({
                        "query": args.get("query", ""),
                        "count": args.get("limit", 5),
                        "papers": []
                    })
                )
            )
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            # Execute workflow
            await run_research_agent(prompt)
            
            # Verify reproducibility (same steps executed each time)
            assert len(execution_log) == 4
            assert mock_client.chat.completions.create.call_count == 4
            
            # Verify consistent tool routing
            tool_calls = [call for call in execution_log if "Step" in call]
            assert len(tool_calls) == 4

    @pytest.mark.e2e
    async def test_error_resilient_research_workflow(self):
        """Test research workflow with error resilience"""
        prompt = """
        Act as an expert researcher.
        
        Execute a resilient research workflow:
        1. Use `search_pubmed` to find papers on "error handling AI biomedical"
        2. If search fails, retry with alternative query
        3. Fetch abstracts for successful results
        4. Save analysis to `research_outputs/resilient_research.md`
        """
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track error handling
            error_handling_log = []
            
            def create_resilient_response(step):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                
                if step == 0:  # First attempt (will fail)
                    mock_response.choices[0].message.content = "I'll search PubMed for error handling papers"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="search_tool",
                        function=Mock(
                            name="search_pubmed",
                            arguments='{"query": "error handling AI biomedical", "limit": 5}'
                        )
                    )]
                elif step == 1:  # Retry attempt
                    mock_response.choices[0].message.content = "Previous search failed, trying alternative query"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="retry_search",
                        function=Mock(
                            name="search_pubmed",
                            arguments='{"query": "AI biomedical error resilience", "limit": 5}'
                        )
                    )]
                elif step == 2:  # Abstract fetching
                    mock_response.choices[0].message.content = "Success! Now fetching abstracts"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="abstract_tool",
                        function=Mock(
                            name="fetch_pubmed_abstracts",
                            arguments='{"pmids": ["1234567", "2345678"]}'
                        )
                    )]
                else:  # Final save
                    mock_response.choices[0].message.content = "Resilient research workflow completed"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="save_tool",
                        function=Mock(
                            name="write_file",
                            arguments='{"path": "research_outputs/resilient_research.md", "content": "# Resilient Research\\n..."}'
                        )
                    )]
                
                return mock_response
            
            responses = [create_resilient_response(i) for i in range(4)]
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers with error simulation
            mock_pubmed_session = MockPubmedServer()
            mock_fs_session = MockFilesystemServer()
            
            call_count = 0
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock server with error handling
            def mock_server_call(tool_name, args):
                nonlocal call_count
                call_count += 1
                
                if tool_name == "search_pubmed" and call_count == 1:
                    # Simulate error on first search
                    error_handling_log.append("First search failed - retrying")
                    raise Exception("Network error - retrying")
                else:
                    # Subsequent calls succeed
                    error_handling_log.append(f"Success: {tool_name}")
                    return Mock(content=json.dumps({"success": True}))
            
            mock_pubmed_session.call_tool = AsyncMock(side_effect=mock_server_call)
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            # Execute workflow
            await run_research_agent(prompt)
            
            # Verify error handling
            assert len(error_handling_log) >= 2  # Should handle at least one error
            assert "failed" in str(error_handling_log[0]).lower()
            assert "success" in str(error_handling_log[1]).lower()

    @pytest.mark.e2e
    async def test_performance_optimized_research_workflow(self):
        """Test performance-optimized research workflow"""
        prompt = """
        Act as an expert performance optimization researcher.
        
        Execute an optimized research workflow:
        1. Use `search_pubmed` to find 10 papers on "performance optimization machine learning"
        2. Use `search_semantic_scholar` concurrently to find 5 papers on "efficient AI algorithms"
        3. Fetch abstracts from both sources in parallel
        4. Save consolidated analysis to `research_outputs/performance_analysis.md`
        5. Include performance metrics and optimization recommendations
        """
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track performance metrics
            performance_log = []
            start_time = asyncio.get_event_loop().time()
            
            def create_performance_response(step):
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                
                performance_log.append(f"Step {step + 1}")
                
                if step == 0:  # Concurrent searches
                    mock_response.choices[0].message.content = "Starting concurrent searches for performance optimization"
                    mock_response.choices[0].message.tool_calls = [
                        Mock(
                            id="pubmed_search",
                            function=Mock(
                                name="search_pubmed",
                                arguments='{"query": "performance optimization machine learning", "limit": 10}'
                            )
                        ),
                        Mock(
                            id="ss_search",
                            function=Mock(
                                name="search_semantic_scholar",
                                arguments='{"query": "efficient AI algorithms", "limit": 5}'
                            )
                        )
                    ]
                elif step == 1:  # Abstract fetching
                    mock_response.choices[0].message.content = "Fetching abstracts in parallel"
                    mock_response.choices[0].message.tool_calls = [
                        Mock(
                            id="pubmed_abstracts",
                            function=Mock(
                                name="fetch_pubmed_abstracts",
                                arguments='{"pmids": ["1234567", "2345678", "3456789", "4567890", "5678901"]}'
                            )
                        ),
                        Mock(
                            id="ss_abstracts",
                            function=Mock(
                                name="fetch_pubmed_abstracts",
                                arguments='{"pmids": ["6789012", "7890123", "8901234", "9012345", "0123456"]}'
                            )
                        )
                    ]
                elif step == 2:  # File saving
                    mock_response.choices[0].message.content = "Saving performance analysis"
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id="save_file",
                        function=Mock(
                            name="write_file",
                            arguments='{"path": "research_outputs/performance_analysis.md", "content": "# Performance Analysis\\n..."}'
                        )
                    )]
                else:  # Final response
                    mock_response.choices[0].message.content = "Performance-optimized research completed"
                    mock_response.choices[0].message.tool_calls = None
                
                return mock_response
            
            responses = [create_performance_response(i) for i in range(4)]
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_ss_session = MockSemanticScholarServer()
            mock_fs_session = MockFilesystemServer()
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "semantic_scholar" in str(args):
                    return mock_ss_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_ss_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock fast server responses
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({"query": args.get("query", ""), "count": args.get("limit", 5)})
                )
            )
            mock_ss_session.call_tool = AsyncMock(
                side_effect=lambda tool_name, args: Mock(
                    content=json.dumps({"query": args.get("query", ""), "count": args.get("limit", 5)})
                )
            )
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            # Execute workflow
            await run_research_agent(prompt)
            
            # Measure performance
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # Verify performance optimization
            assert mock_client.chat.completions.create.call_count == 4
            assert len(performance_log) == 4
            
            # Performance assertion (should complete within reasonable time)
            assert execution_time < 20  # Should complete within 20 seconds
            
            # Verify concurrent execution was used
            concurrent_steps = [step for step in performance_log if "concurrent" in step.lower() or "parallel" in step.lower()]
            assert len(concurrent_steps) > 0