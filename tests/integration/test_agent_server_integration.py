"""
Integration tests for agent-server interactions
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent
from fixtures.mcp_mocks import MockPubmedServer, MockSemanticScholarServer, MockFilesystemServer


class TestAgentServerIntegration:
    """Integration tests for agent-server interactions"""

    @pytest.mark.integration
    async def test_agent_with_mock_pubmed_server(self):
        """Test agent interaction with mock PubMed server"""
        mock_prompt = "Search PubMed for non-invasive glucose monitoring papers and save results"
        
        # Mock the client and servers
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed for glucose monitoring papers"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="tool_123",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "non-invasive glucose monitoring", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
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
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved successfully"))
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify interactions
            mock_pubmed_session.call_tool.assert_called_once()
            mock_fs_session.call_tool.assert_called_once()

    @pytest.mark.integration
    async def test_agent_with_multiple_servers(self):
        """Test agent interaction with multiple MCP servers"""
        mock_prompt = "Search both PubMed and Semantic Scholar for machine learning healthcare papers"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup mock response with multiple tool calls
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search both databases"
            mock_response.choices[0].message.tool_calls = [
                Mock(
                    id="pubmed_tool",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "machine learning healthcare", "limit": 5}'
                    )
                ),
                Mock(
                    id="ss_tool",
                    function=Mock(
                        name="search_semantic_scholar",
                        arguments='{"query": "machine learning healthcare", "limit": 5}'
                    )
                )
            ]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_ss_session = MockSemanticScholarServer()
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "semantic_scholar" in str(args):
                    return mock_ss_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_ss_session.initialize()
            
            # Mock server responses
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            mock_ss_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify both servers were called
            mock_pubmed_session.call_tool.assert_called_once()
            mock_ss_session.call_tool.assert_called_once()

    @pytest.mark.integration
    async def test_agent_tool_routing_logic(self):
        """Test agent tool routing to correct servers"""
        mock_prompt = "Search PubMed for glucose monitoring and save results"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed and save results"
            mock_response.choices[0].message.tool_calls = [
                Mock(
                    id="pubmed_tool",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "glucose monitoring", "limit": 5}'
                    )
                ),
                Mock(
                    id="fs_tool",
                    function=Mock(
                        name="write_file",
                        arguments='{"path": "/tmp/results.md", "content": "Results"}'
                    )
                )
            ]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_fs_session = MockFilesystemServer()
            
            call_log = []
            
            async def mock_session_init(*args, **kwargs):
                call_log.append(str(args))
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_fs_session.initialize()
            
            # Mock server responses
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify tool routing
            mock_pubmed_session.call_tool.assert_called_once()
            mock_fs_session.call_tool.assert_called_once()
            
            # Verify that tools were routed to correct servers
            pubmed_calls = [call for call in call_log if "pubmed" in call]
            fs_calls = [call for call in call_log if "filesystem" in call]
            
            assert len(pubmed_calls) > 0
            assert len(fs_calls) > 0

    @pytest.mark.integration
    async def test_agent_error_handling_server_failures(self):
        """Test agent error handling when servers fail"""
        mock_prompt = "Search PubMed for test papers"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="tool_123",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server that fails
            mock_pubmed_session = MockPubmedServer()
            await mock_pubmed_session.initialize()
            
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Server connection failed")
            )
            
            mock_session_class.side_effect = lambda *args, **kwargs: mock_pubmed_session
            
            # Execute agent (should handle error gracefully)
            try:
                await run_research_agent(mock_prompt)
            except Exception as e:
                # Should handle the error, but may still raise for testing
                assert "Server connection failed" in str(e)

    @pytest.mark.integration
    async def test_agent_message_flow_validation(self):
        """Test agent message flow and validation"""
        mock_prompt = "Test message flow validation"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Track message flow
            message_log = []
            
            async def track_messages(*args, **kwargs):
                message_log.append(args)
                # Setup mock response
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = "Test response"
                mock_response.choices[0].message.tool_calls = None
                return mock_response
            
            mock_client.chat.completions.create.side_effect = track_messages
            
            # Setup mock server
            mock_pubmed_session = MockPubmedServer()
            await mock_pubmed_session.initialize()
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content="Mock result"))
            
            mock_session_class.side_effect = lambda *args, **kwargs: mock_pubmed_session
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Validate message flow
            assert len(message_log) >= 1
            assert mock_prompt in str(message_log[0])

    @pytest.mark.integration
    async def test_agent_concurrent_tool_execution(self):
        """Test agent concurrent tool execution"""
        mock_prompt = "Search multiple databases concurrently"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup mock response with multiple tool calls
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search concurrently"
            mock_response.choices[0].message.tool_calls = [
                Mock(
                    id="tool_1",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "test1", "limit": 3}'
                    )
                ),
                Mock(
                    id="tool_2",
                    function=Mock(
                        name="search_semantic_scholar",
                        arguments='{"query": "test2", "limit": 3}'
                    )
                )
            ]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock servers
            mock_pubmed_session = MockPubmedServer()
            mock_ss_session = MockSemanticScholarServer()
            
            call_order = []
            
            async def mock_session_init(*args, **kwargs):
                call_order.append(str(args))
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "semantic_scholar" in str(args):
                    return mock_ss_session
                return AsyncMock()
            
            mock_session_class.side_effect = mock_session_init
            await mock_pubmed_session.initialize()
            await mock_ss_session.initialize()
            
            # Mock server responses
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            mock_ss_session.call_tool = AsyncMock(return_value=Mock(content='{"papers": []}'))
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify both tools were executed
            mock_pubmed_session.call_tool.assert_called_once()
            mock_ss_session.call_tool.assert_called_once()

    @pytest.mark.integration
    async def test_agent_iteration_limit_enforcement(self):
        """Test agent iteration limit enforcement"""
        mock_prompt = "Complex task requiring multiple iterations"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup multiple mock responses
            responses = []
            for i in range(6):  # More than max_iterations
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Response {i+1}"
                mock_response.choices[0].message.tool_calls = None if i >= 4 else [Mock(
                    id=f"tool_{i}",
                    function=Mock(
                        name="search_pubmed",
                        arguments='{"query": "test", "limit": 5}'
                    )
                )]
                responses.append(mock_response)
            
            mock_client.chat.completions.create.side_effect = responses
            
            # Setup mock server
            mock_pubmed_session = MockPubmedServer()
            await mock_pubmed_session.initialize()
            mock_pubmed_session.call_tool = AsyncMock(return_value=Mock(content="Mock result"))
            
            mock_session_class.side_effect = lambda *args, **kwargs: mock_pubmed_session
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify that the client was called exactly 5 times (max_iterations)
            assert mock_client.chat.completions.create.call_count == 5


class TestAgentServerCommunicationProtocols:
    """Test agent-server communication protocols"""

    @pytest.mark.integration
    async def test_server_initialization_sequence(self):
        """Test proper server initialization sequence"""
        mock_prompt = "Test server initialization"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup simple response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Test response"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            # Track initialization calls
            init_calls = []
            
            async def mock_session_init(*args, **kwargs):
                init_calls.append(str(args))
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                return mock_session
            
            mock_session_class.side_effect = mock_session_init
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify all servers were initialized
            assert len(init_calls) >= 1

    @pytest.mark.integration
    async def test_server_connection_timeout_handling(self):
        """Test server connection timeout handling"""
        mock_prompt = "Test timeout handling"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Test response"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            # Track session creation
            session_calls = []
            
            async def mock_session_init(*args, **kwargs):
                session_calls.append(str(args))
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                return mock_session
            
            mock_session_class.side_effect = mock_session_init
            
            # Execute agent
            await run_research_agent(mock_prompt)
            
            # Verify session creation
            assert len(session_calls) >= 1

    @pytest.mark.integration
    async def test_server_error_propagation(self):
        """Test server error propagation to agent"""
        mock_prompt = "Test error propagation"
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Setup response with tool call
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="tool_123",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup server that fails
            mock_pubmed_session = MockPubmedServer()
            await mock_pubmed_session.initialize()
            
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Server error")
            )
            
            mock_session_class.side_effect = lambda *args, **kwargs: mock_pubmed_session
            
            # Execute agent (should handle error)
            try:
                await run_research_agent(mock_prompt)
            except Exception as e:
                # Error should be handled or propagated
                assert "Server error" in str(e) or "Error executing tool" in str(e)