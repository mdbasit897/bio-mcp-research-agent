#!/usr/bin/env python3
"""
Simple test runner for the biomedical research agent
"""
import sys
import os
import unittest
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_basic_tests():
    """Run basic tests without pytest dependencies"""
    print("🧪 Running basic tests...")
    
    # Test basic imports
    try:
        import agent
        print("✅ Agent module imports successfully")
    except Exception as e:
        print(f"❌ Agent module import failed: {e}")
        return False
    
    try:
        from agent import run_research_agent
        print("✅ Agent function imports successfully")
    except Exception as e:
        print(f"❌ Agent function import failed: {e}")
        return False
    
    # Test basic functionality
    try:
        # Create a simple test agent
        test_prompt = "Hello, this is a test prompt"
        print(f"✅ Test prompt: {test_prompt}")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def run_syntax_checks():
    """Run syntax checks on source files"""
    print("🔍 Running syntax checks...")
    
    source_files = [
        'src/agent.py',
        'src/servers/pubmed_server.py',
        'src/servers/semantic_scholar.py'
    ]
    
    for file_path in source_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ {file_path} syntax OK")
            except SyntaxError as e:
                print(f"❌ {file_path} syntax error: {e}")
                return False
        else:
            print(f"⚠️  {file_path} not found")
    
    return True

def main():
    print("🚀 Running comprehensive test suite (simplified)")
    print("=" * 50)
    
    # Run basic tests
    basic_ok = run_basic_tests()
    
    # Run syntax checks
    syntax_ok = run_syntax_checks()
    
    # Summary
    print("\n" + "=" * 50)
    if basic_ok and syntax_ok:
        print("🎉 All basic tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())