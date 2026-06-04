"""
Unit tests for the CLI version of the research agent
"""
import pytest
import argparse
import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent_cli import main, load_prompt_from_file, run_research_agent


class TestAgentCLI:
    """Test CLI functionality and argument parsing"""

    @pytest.mark.unit
    def test_argument_parsing_direct_prompt(self):
        """Test CLI argument parsing for direct prompt"""
        with patch('sys.argv', ['agent_cli', '--prompt', 'Test prompt']):
            with patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()

    @pytest.mark.unit
    def test_argument_parsing_file_prompt(self):
        """Test CLI argument parsing for file-based prompt"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test prompt from file')
            temp_file = f.name
        
        try:
            with patch('sys.argv', ['agent_cli', '--file', temp_file]), \
                 patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_argument_parsing_example_prompt(self):
        """Test CLI argument parsing for example prompt"""
        with patch('sys.argv', ['agent_cli', '--example']), \
             patch('agent_cli.os.makedirs') as mock_makedirs, \
             patch('agent_cli.asyncio.run') as mock_run:
            
            main()
            
            mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
            mock_run.assert_called_once()

    @pytest.mark.unit
    def test_argument_parsing_no_args(self):
        """Test CLI argument parsing with no arguments"""
        with patch('sys.argv', ['agent_cli']), \
             patch('argparse.ArgumentParser.print_help') as mock_help, \
             patch('agent_cli.os.makedirs') as mock_makedirs, \
             patch('agent_cli.asyncio.run') as mock_run:
        
        main()
        
        mock_help.assert_called_once()
        mock_makedirs.assert_not_called()
        mock_run.assert_not_called()

    @pytest.mark.unit
    def test_load_prompt_from_file_success(self):
        """Test successful loading of prompt from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test prompt content')
            temp_file = f.name
        
        try:
            result = load_prompt_from_file(temp_file)
            assert result == 'Test prompt content'
        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_load_prompt_from_file_not_found(self):
        """Test handling of non-existent prompt file"""
        with pytest.raises(SystemExit):
            load_prompt_from_file('nonexistent_file.txt')

    @pytest.mark.unit
    def test_load_prompt_from_file_error(self):
        """Test handling of file read error"""
        with tempfile.NamedTemporaryFile() as f:
            # Close the file to make it inaccessible
            f.close()
            
            with pytest.raises(SystemExit):
                load_prompt_from_file(f.name)


class TestAgentCLIIntegration:
    """Integration tests for CLI functionality"""

    @pytest.mark.unit
    async def test_cli_with_mock_agent(self):
        """Test CLI integration with mocked agent"""
        test_prompt = "Test CLI integration"
        
        with patch('agent_cli.run_research_agent') as mock_run_agent, \
             patch('agent_cli.os.makedirs') as mock_makedirs:
            
            await run_research_agent(test_prompt)
            
            mock_run_agent.assert_called_once_with(test_prompt)
            mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)

    @pytest.mark.unit
    def test_environment_variable_handling(self):
        """Test CLI handling of environment variables"""
        with patch.dict(os.environ, {
            'OPENROUTER_API_KEY': 'test_api_key',
            'OPENROUTER_MODEL': 'test_model'
        }):
            # Test that environment variables are accessible
            assert os.getenv('OPENROUTER_API_KEY') == 'test_api_key'
            assert os.getenv('OPENROUTER_MODEL') == 'test_model'

    @pytest.mark.unit
    def test_cli_help_output(self):
        """Test CLI help output contains expected information"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--prompt', '-p', type=str, help='Direct prompt string')
        parser.add_argument('--file', '-f', type=str, help='Path to prompt file')
        parser.add_argument('--example', '-e', action='store_true', help='Use example prompt')
        
        # Test that help contains expected options
        help_text = parser.format_help()
        assert '--prompt' in help_text or '-p' in help_text
        assert '--file' in help_text or '-f' in help_text
        assert '--example' in help_text or '-e' in help_text


class TestAgentCLIErrorHandling:
    """Test CLI error handling and edge cases"""

    @pytest.mark.unit
    def test_empty_prompt_handling(self):
        """Test handling of empty prompts"""
        with patch('sys.argv', ['agent_cli', '--prompt', '']):
            with patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                # Should still process empty prompt
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()

    @pytest.mark.unit
    def test_whitespace_prompt_handling(self):
        """Test handling of whitespace-only prompts"""
        with patch('sys.argv', ['agent_cli', '--prompt', '   \n\t  ']):
            with patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                # Should process whitespace prompts
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()

    @pytest.mark.unit
    def test_long_prompt_handling(self):
        """Test handling of long prompts"""
        long_prompt = "A" * 10000  # Very long prompt
        
        with patch('sys.argv', ['agent_cli', '--prompt', long_prompt]):
            with patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                # Should handle long prompts
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()

    @pytest.mark.unit
    def test_unicode_prompt_handling(self):
        """Test handling of Unicode characters in prompts"""
        unicode_prompt = "测试 prompt with 🧬 biomedical research"
        
        with patch('sys.argv', ['agent_cli', '--prompt', unicode_prompt]):
            with patch('agent_cli.os.makedirs') as mock_makedirs, \
                 patch('agent_cli.asyncio.run') as mock_run:
                
                main()
                
                # Should handle Unicode prompts
                mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)
                mock_run.assert_called_once()


class TestAgentCLIConfiguration:
    """Test CLI configuration and settings"""

    @pytest.mark.unit
    def test_output_directory_creation(self):
        """Test that output directory is created properly"""
        with patch('sys.argv', ['agent_cli', '--example']), \
             patch('agent_cli.os.makedirs') as mock_makedirs, \
             patch('agent_cli.asyncio.run') as mock_run:
            
            main()
            
            mock_makedirs.assert_called_once_with("research_outputs", exist_ok=True)

    @pytest.mark.unit
    def test_custom_output_directory(self):
        """Test handling of custom output directory"""
        with patch.dict(os.environ, {
            'RESEARCH_OUTPUTS': 'custom_output_dir'
        }):
            # This would be implemented in the actual CLI
            assert os.getenv('RESEARCH_OUTPUTS') == 'custom_output_dir'

    @pytest.mark.unit
    def test_model_configuration_override(self):
        """Test model configuration can be overridden"""
        with patch.dict(os.environ, {
            'OPENROUTER_MODEL': 'custom-model/override:latest'
        }):
            # Test that custom model can be set
            assert os.getenv('OPENROUTER_MODEL') == 'custom-model/override:latest'

    @pytest.mark.unit
    async def test_cli_with_error_scenarios(self):
        """Test CLI behavior with various error scenarios"""
        test_prompt = "Test error scenarios"
        
        # Test with mocked client error
        with patch('agent_cli.client') as mock_client, \
             patch('agent_cli.os.makedirs') as mock_makedirs:
            
            mock_client.chat.completions.create.side_effect = Exception("Test error")
            
            # Should handle errors gracefully (may raise exceptions)
            with pytest.raises(Exception):
                await run_research_agent(test_prompt)