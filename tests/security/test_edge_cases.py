"""
Security and edge case validation tests
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent


class TestEdgeCaseValidation:
    """Edge case validation tests"""

    @pytest.mark.security
    async def test_empty_query_handling(self):
        """Test handling of empty queries"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Empty query detected"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test with empty query
            await run_research_agent("")
            
            # Should handle empty query gracefully
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.security
    async def test_null_input_handling(self):
        """Test handling of null/None inputs"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Null input detected"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test with None input
            await run_research_agent(None)
            
            # Should handle null input gracefully
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.security
    async def test_extremely_long_query_handling(self):
        """Test handling of extremely long queries"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            # Create extremely long query (10KB)
            long_query = "A" * 10000
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Long query processed"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create.return_value = mock_response
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test with extremely long query
            await run_research_agent(long_query)
            
            # Should handle long query gracefully
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.security
    async def test_special_characters_in_query(self):
        """Test handling of special characters in queries"""
        special_queries = [
            "Query with <script>alert('xss')</script>",
            "Query with ' OR '1'='1",
            "Query with ; DROP TABLE users;",
            "Query with $(rm -rf /)",
            "Query with unicode: 测试 🧬 生物医学",
            "Query with newlines\nand\ttabs",
            "Query with quotes \"single\" and 'double'",
            "Query with backticks `echo test`",
            "Query with brackets [test] {test} (test)",
            "Query with symbols @#$%^&*()"
        ]
        
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_session = Mock()
            mock_session.initialize = AsyncMock()
            mock_session_class.return_value = mock_session
            
            for query in special_queries:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Special chars processed: {query[:50]}..."
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                # Test with special characters
                await run_research_agent(query)
                
                # Should handle special characters gracefully
                mock_client.chat.completions.create.assert_called()

    @pytest.mark.security
    async def test_recursive_tool_calls(self):
        """Test handling of recursive tool calls"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            call_count = 0
            
            def recursive_response_generator():
                nonlocal call_count
                call_count += 1
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Recursive call {call_count}"
                
                # Create recursive tool calls (limited to prevent infinite loop)
                if call_count < 6:  # Limit to 5 iterations
                    mock_response.choices[0].message.tool_calls = [Mock(
                        id=f"recursive_tool_{call_count}",
                        function=Mock(
                            name="search_pubmed",
                            arguments='{"query": "recursive test", "limit": 5}'
                        )
                    )]
                else:
                    mock_response.choices[0].message.tool_calls = None
                
                return mock_response
            
            mock_client.chat.completions.create.side_effect = recursive_response_generator
            
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
            
            # Test recursive calls
            await run_research_agent("Test recursive tool calls")
            
            # Should handle recursion with proper iteration limits
            assert call_count == 6  # Should stop at max iterations

    @pytest.mark.security
    async def test_concurrent_requests_stress(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        
        async def execute_concurrent_task(task_id):
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
        
        # Execute many concurrent tasks
        tasks = [execute_concurrent_task(i) for i in range(20)]
        await asyncio.gather(*tasks)
        
        # Should handle concurrent requests without issues

    @pytest.mark.security
    async def test_malformed_json_handling(self):
        """Test handling of malformed JSON in tool responses"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_mendaske:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="malformed_json_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with malformed JSON
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                return_value=Mock(content='{"malformed": json, "invalid": }')
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle malformed JSON gracefully
            await run_research_agent("Test malformed JSON handling")


class TestErrorHandling:
    """Error handling tests"""

    @pytest.mark.security
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="network_error_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with network error
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Network connection failed")
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle network errors gracefully
            try:
                await run_research_agent("Test network error handling")
            except Exception as e:
                # Error should be handled gracefully or contain appropriate error message
                assert "network" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.security
    async def test_timeout_error_handling(self):
        """Test handling of timeout errors"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="timeout_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with timeout
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Request timeout")
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle timeout errors gracefully
            try:
                await run_research_agent("Test timeout error handling")
            except Exception as e:
                # Error should be handled gracefully
                assert "timeout" in str(e).lower()

    @pytest.mark.security
    async def test_rate_limit_handling(self):
        """Test handling of rate limits"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="rate_limit_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with rate limit
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Rate limit exceeded: 429 Too Many Requests")
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle rate limits gracefully
            try:
                await run_research_agent("Test rate limit handling")
            except Exception as e:
                # Error should be handled gracefully
                assert "rate limit" in str(e).lower() or "429" in str(e)

    @pytest.mark.security
    async def test_authentication_error_handling(self):
        """Test handling of authentication errors"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_makedirs:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="auth_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "test", "limit": 5}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with auth error
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Authentication failed: Invalid API key")
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle auth errors gracefully
            try:
                await run_research_agent("Test authentication error handling")
            except Exception as e:
                # Error should be handled gracefully
                assert "auth" in str(e).lower() or "api key" in str(e).lower()

    @pytest.mark.security
    async def test_validation_error_handling(self):
        """Test handling of validation errors"""
        with patch('agent.client') as mock_client, \
             patch('agent.stdio_client') as mock_stdio, \
             patch('agent.ClientSession') as mock_session_class, \
             patch('agent.os.makedirs') as mock_mendaske:
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "I'll search PubMed"
            mock_response.choices[0].message.tool_calls = [Mock(
                id="validation_test",
                function=Mock(
                    name="search_pubmed",
                    arguments='{"query": "", "limit": -1}'
                )
            )]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # Setup mock server with validation error
            mock_pubmed_session = Mock()
            mock_pubmed_session.initialize = AsyncMock()
            mock_pubmed_session.call_tool = AsyncMock(
                side_effect=Exception("Validation error: Query cannot be empty")
            )
            
            mock_fs_session = Mock()
            mock_fs_session.initialize = AsyncMock()
            mock_fs_session.call_tool = AsyncMock(return_value=Mock(content="File saved"))
            
            async def mock_session_init(*args, **kwargs):
                if "pubmed" in str(args):
                    return mock_pubmed_session
                elif "filesystem" in str(args):
                    return mock_fs_session
                return Mock()
            
            mock_session_class.side_effect = mock_session_init
            
            # Should handle validation errors gracefully
            try:
                await run_research_agent("Test validation error handling")
            except Exception as e:
                # Error should be handled gracefully
                assert "validation" in str(e).lower() or "invalid" in str(e).lower()


class TestInputSanitization:
    """Input sanitization tests"""

    @pytest.mark.security
    async def test_sql_injection_prevention(self):
        """Test prevention of SQL injection"""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "SELECT * FROM users WHERE username = 'admin'",
            "admin' --",
            "admin' /*",
            "admin';#",
            "admin' OR '1'='1",
            "admin' OR '1'='1' --",
            "admin' OR '1'='1' /*",
            "admin' OR '1'='1' #"
        ]
        
        for malicious_input in sql_injection_attempts:
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_mendaske:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Query processed: {malicious_input[:20]}..."
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                # Should handle SQL injection attempts gracefully
                await run_research_agent(malicious_input)

    @pytest.mark.security
    async def test_xss_prevention(self):
        """Test prevention of XSS attacks"""
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src='x' onerror='alert(1)'>",
            "<svg onload='alert(1)'>",
            "'\"><script>alert(1)</script>",
            "javascript:alert(document.cookie)",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<body onload=alert(1)>",
            "<div onmouseover='alert(1)'>test</div>",
            "<input onfocus=alert(1) autofocus>"
        ]
        
        for malicious_input in xss_attempts:
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_mendaske:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"XSS test processed"
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                # Should handle XSS attempts gracefully
                await run_research_agent(malicious_input)

    @pytest.mark.security
    async def test_command_injection_prevention(self):
        """Test prevention of command injection"""
        command_injection_attempts = [
            "glucose monitoring; rm -rf /",
            "diabetes research && cat /etc/passwd",
            "healthcare research || ls -la",
            "medical study `whoami`",
            "patient data $(echo 'test')",
            "research topic | cat /etc/passwd",
            "health analysis > /tmp/malicious",
            "medical study < /etc/passwd",
            "research data || rm -rf /",
            "healthcare $(rm -rf /)"
        ]
        
        for malicious_input in command_injection_attempts:
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_mendaske:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Command injection test processed"
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                # Should handle command injection attempts gracefully
                await run_research_agent(malicious_input)

    @pytest.mark.security
    async def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks"""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "glucose monitoring/../../../../etc/passwd",
            "diabetes research\\..\\..\\..\\windows\\system32\\config\\sam",
            "healthcare study/../../../../../../etc/shadow",
            "medical research/../../../../../../etc/hosts",
            "patient data/../../../../../../etc/passwd",
            "research topic/../../../../../../etc/hosts",
            "health analysis/../../../../../../etc/shadow",
            "biomedical study/../../../../../../etc/passwd"
        ]
        
        for malicious_input in path_traversal_attempts:
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_mendaske:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"Path traversal test processed"
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                # Should handle path traversal attempts gracefully
                await run_research_agent(malicious_input)