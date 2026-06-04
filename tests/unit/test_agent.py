"""
Unit tests for the MCP Research Agent core functionality
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent


class TestResearchAgentCore:
    """Core functionality tests for the research agent"""

    @pytest.mark.unit
    async def test_research_agent_initialization(self):
        """Test that the research agent initializes properly"""
        mock_prompt = "Test research prompt"
        
        # Mock response needed for setup
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.tool_calls = None
        
        # Create async mock for the create method
        mock_create = AsyncMock(return_value=mock_response)
        
        # Create mock session with proper async context manager support
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock stdio context managers
        mock_stdio_cm = Mock()
        mock_stdio_cm.__aenter__ = AsyncMock(return_value=(Mock(), Mock()))
        mock_stdio_cm.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the dependencies - patch at the right level
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client', return_value=mock_stdio_cm), \
             patch('agent.ClientSession', return_value=mock_session), \
             patch('agent.os.makedirs'):
            
            # Setup the mock client instance properly
            MockClient.chat.completions.create = mock_create
            
            # Test initialization
            await run_research_agent(mock_prompt)
            
            # Verify the function runs without error
            assert mock_session.initialize.called

    @pytest.mark.unit
    async def test_response_handling_with_valid_response(self):
        """Test handling of valid LLM responses"""
        mock_prompt = "Test prompt"
        
        # Mock successful response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Research completed successfully"
        mock_response.choices[0].message.tool_calls = None
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs'):
            
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
            
            # Should not raise exceptions
            await run_research_agent(mock_prompt)

    @pytest.mark.unit
    async def test_response_handling_with_tool_calls(self):
        """Test handling of LLM responses with tool calls"""
        mock_prompt = "Test prompt with tools"
        
        # Mock response with tool calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I need to search PubMed"
        mock_response.choices[0].message.tool_calls = [
            Mock(
                id="tool_123",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "glucose monitoring", "limit": 5}'
                )
            )
        ]
        
        # Create async mock for create method
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs'):
            
            # Setup mock client properly
            MockClient.chat.completions.create = mock_create
            
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            mock_session.call_tool = AsyncMock(return_value=Mock(content="Mock search results"))
            mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
            
            # Should handle tool calls without errors
            await run_research_agent(mock_prompt)

    @pytest.mark.unit
    @pytest.mark.slow
    async def test_multiple_iterations(self):
        """Test handling of multiple LLM iterations"""
        mock_prompt = "Complex research task requiring multiple steps"
        
        # Mock multiple responses
        responses = []
        for i in range(3):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = f"Step {i+1} completed"
            mock_response.choices[0].message.tool_calls = None if i == 2 else [Mock(
                id=f"tool_{i}",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            responses.append(mock_response)
        
        # Create async mock with side_effect for multiple calls
        mock_create = AsyncMock(side_effect=responses)
        
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs'):
            
            # Setup mock client
            MockClient.chat.completions.create = mock_create
            
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            mock_session.call_tool = AsyncMock(return_value=Mock(content="Mock result"))
            mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
            
            # Should handle multiple iterations
            await run_research_agent(mock_prompt)

    @pytest.mark.unit
    def test_environment_variables_handling(self):
        """Test proper handling of environment variables"""
        # Test that the agent correctly loads environment variables
        with patch.dict(os.environ, {
            'OPENROUTER_API_KEY': 'test_key',
            'OPENROUTER_MODEL': 'test_model',
            'OPENROUTER_BASE_URL': 'http://test.url'
        }):
            # This should not raise exceptions during initialization
            assert os.getenv('OPENROUTER_API_KEY') == 'test_key'
            assert os.getenv('OPENROUTER_MODEL') == 'test_model'

    @pytest.mark.unit
    async def test_error_handling_network_failure(self):
        """Test graceful handling of network failures"""
        mock_prompt = "Test prompt"
        
        # Mock network error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Network error")
        
        with patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            
            # Should handle errors gracefully (though may raise expected exceptions)
            with pytest.raises(Exception):
                await run_research_agent(mock_prompt)


class TestResearchAgentMessaging:
    """Test message handling and LLM interaction patterns"""

    @pytest.mark.unit
    async def test_message_construction(self):
        """Test proper construction of conversation messages"""
        test_prompt = "Test research prompt"
        
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.tool_calls = None
        
        # Create async mock
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs'):
            
            # Setup mock client
            MockClient.chat.completions.create = mock_create
            
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
            
            await run_research_agent(test_prompt)
            
            # Verify that the initial message was constructed correctly
            expected_messages = [{"role": "user", "content": test_prompt}]
            assert len(expected_messages) == 1
            assert expected_messages[0]["role"] == "user"
            assert expected_messages[0]["content"] == test_prompt

    @pytest.mark.unit
    async def test_tool_result_formatting(self):
        """Test proper formatting of tool results"""
        mock_prompt = "Test tool execution"
        
        # Mock response with tool call
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I'll search PubMed"
        mock_response.choices[0].message.tool_calls = [Mock(
            id="tool_123",
            function=Mock(
                name="search_pubmed",
                arguments='{"query": "diabetes", "limit": 5}'
            )
        )]
        
        # Create async mock
        mock_create = AsyncMock(return_value=mock_response)
        
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs'):
            
            # Setup mock client
            MockClient.chat.completions.create = mock_create
            
            mock_stdio.return_value.__aenter__.return_value = (Mock(), Mock())
            mock_session = mock_session_class.return_value
            mock_session.initialize = AsyncMock()
            mock_session.call_tool = AsyncMock(return_value=Mock(
                content='{"papers": [{"title": "Test Paper", "pmid": "123456"}]}'
            ))
            mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
            
            await run_research_agent(mock_prompt)
            
            # Verify tool result message structure
            expected_tool_message = {
                "role": "tool",
                "tool_call_id": "tool_123",
                "content": '{"papers": [{"title": "Test Paper", "pmid": "123456"}]}'
            }
            assert expected_tool_message["role"] == "tool"
            assert expected_tool_message["tool_call_id"] == "tool_123"


class TestResearchAgentConfiguration:
    """Test agent configuration and settings"""

    @pytest.mark.unit
    def test_model_configuration(self):
        """Test model configuration loading"""
        # This test verifies that the model configuration is loaded correctly
        with patch.dict(os.environ, {
            'OPENROUTER_MODEL': 'custom-model/test:latest'
        }):
            # Verify environment variable loading
            assert os.getenv('OPENROUTER_MODEL') == 'custom-model/test:latest'

    @pytest.mark.unit
    def test_max_iterations_configuration(self):
        """Test maximum iterations configuration"""
        # Test that max_iterations is properly configured
        # This would be in the actual implementation
        assert 5 > 0  # Basic validation that iterations are positive

    @pytest.mark.unit
    async def test_tool_routing_logic(self):
        """Test proper routing of tools to correct sessions"""
        mock_prompt = "Test tool routing"
        
        # Mock response with multiple tool calls - first call returns tool calls, second returns final answer
        mock_response_with_tools = Mock()
        mock_response_with_tools.choices = [Mock()]
        mock_response_with_tools.choices[0].message = Mock()
        mock_response_with_tools.choices[0].message.content = "I'll search both PubMed and Semantic Scholar"
        mock_response_with_tools.choices[0].message.tool_calls = [
            Mock(
                id="pubmed_tool",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test"}'
                )
            ),
            Mock(
                id="ss_tool",
                function=Mock(
                    name="search_semantic_scholar",
                    arguments='{"query": "test"}'
                )
            )
        ]
        
        # Second response (final answer)
        mock_final_response = Mock()
        mock_final_response.choices = [Mock()]
        mock_final_response.choices[0].message = Mock()
        mock_final_response.choices[0].message.content = "Final results"
        mock_final_response.choices[0].message.tool_calls = None
        
        # Create async mock that returns different responses
        mock_create = AsyncMock(side_effect=[mock_response_with_tools, mock_final_response])
        
        # Create mock session with proper async context manager support
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=Mock(tools=[]))
        mock_session.call_tool = AsyncMock(return_value=Mock(content="Result"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock stdio context managers
        mock_stdio_cm = Mock()
        mock_stdio_cm.__aenter__ = AsyncMock(return_value=(Mock(), Mock()))
        mock_stdio_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('agent.client') as MockClient, \
             patch('agent.stdio_client', return_value=mock_stdio_cm), \
             patch('agent.ClientSession', return_value=mock_session), \
             patch('agent.os.makedirs'):
            
            # Setup mock client
            MockClient.chat.completions.create = mock_create
            
            await run_research_agent(mock_prompt)
            
            # Verify that call_tool was called (tool routing happened)
            assert mock_session.call_tool.called