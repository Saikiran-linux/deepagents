#!/usr/bin/env python3
"""
Debug script for the research agent to identify file writing issues.

This script provides detailed debugging information to help identify
why the research agent might not be writing to files.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from research_agent import agent, internet_search, search_specific_sources

async def debug_agent_step_by_step():
    """Debug the agent execution step by step."""
    
    print("🔬 Research Agent Debugging Session")
    print("=" * 50)
    
    # Test 1: Verify agent creation
    print("\n1. Testing agent creation...")
    try:
        print(f"✅ Agent created successfully: {type(agent)}")
        print(f"   Agent tools: {[tool.name for tool in agent.tools if hasattr(tool, 'name')]}")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return
    
    # Test 2: Test simple direct tool usage
    print("\n2. Testing direct tool usage...")
    try:
        # Test write_file tool directly if possible
        from deepagents.tools import write_file
        print("✅ write_file tool imported successfully")
    except Exception as e:
        print(f"❌ Could not import write_file tool: {e}")
    
    # Test 3: Test search tools
    print("\n3. Testing search tools...")
    try:
        search_result = internet_search("test query", max_results=1)
        print(f"✅ Internet search works: Found {len(search_result.get('results', []))} results")
    except Exception as e:
        print(f"❌ Internet search failed: {e}")
    
    # Test 4: Simple agent invocation
    print("\n4. Testing simple agent invocation...")
    simple_question = "What is the capital of France?"
    
    try:
        print(f"Invoking agent with: {simple_question}")
        result = agent.invoke({"messages": [{"role": "user", "content": simple_question}]})
        print(f"✅ Agent invocation completed")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and "messages" in result:
            last_message = result["messages"][-1]
            print(f"   Last message type: {type(last_message)}")
            print(f"   Last message content preview: {str(last_message)[:200]}...")
        
        # Check if files were created
        check_files_created()
        
    except Exception as e:
        print(f"❌ Agent invocation failed: {e}")
        import traceback
        traceback.print_exc()

def check_files_created():
    """Check if expected files were created."""
    print("\n📁 Checking for created files...")
    
    question_file = Path("question.txt")
    report_file = Path("final_report.md")
    
    print(f"question.txt exists: {question_file.exists()}")
    if question_file.exists():
        content = question_file.read_text()
        print(f"  Size: {len(content)} characters")
        print(f"  Content: {content[:100]}...")
    
    print(f"final_report.md exists: {report_file.exists()}")
    if report_file.exists():
        content = report_file.read_text()
        print(f"  Size: {len(content)} characters")
        print(f"  Content preview: {content[:200]}...")
    
    if not question_file.exists() and not report_file.exists():
        print("❌ No files were created - this indicates the issue")
    elif question_file.exists() and not report_file.exists():
        print("⚠️ Only question file created - agent may not be completing research")
    elif question_file.exists() and report_file.exists():
        print("✅ Both files created successfully")

async def test_minimal_research():
    """Test with a minimal research question that should definitely work."""
    
    print("\n🎯 Testing Minimal Research Scenario")
    print("=" * 40)
    
    minimal_question = "What is 2+2?"
    
    print(f"Question: {minimal_question}")
    print("This should be simple enough that the agent can definitely answer it...")
    
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": minimal_question}]
        })
        
        print("✅ Minimal research completed")
        check_files_created()
        
        return result
        
    except Exception as e:
        print(f"❌ Minimal research failed: {e}")
        import traceback
        traceback.print_exc()

async def test_with_explicit_instructions():
    """Test with very explicit file writing instructions."""
    
    print("\n📝 Testing with Explicit File Writing Instructions")
    print("=" * 50)
    
    explicit_instruction = """
I need you to do exactly these steps:
1. Write the text "Test question" to a file called question.txt
2. Write a simple report about what 2+2 equals to a file called final_report.md

Use the write_file tool to create both files. This is a test to see if file writing works.
"""
    
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": explicit_instruction}]
        })
        
        print("✅ Explicit instruction test completed")
        check_files_created()
        
        return result
        
    except Exception as e:
        print(f"❌ Explicit instruction test failed: {e}")
        import traceback
        traceback.print_exc()

def main_debug():
    """Main debug function with menu."""
    
    print("🐛 Research Agent Debug Menu")
    print("=" * 30)
    print("1. Step-by-step debugging")
    print("2. Minimal research test")
    print("3. Explicit file writing test")
    print("4. All tests")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect test (1-5): ").strip()
        
        if choice == '1':
            asyncio.run(debug_agent_step_by_step())
        elif choice == '2':
            asyncio.run(test_minimal_research())
        elif choice == '3':
            asyncio.run(test_with_explicit_instructions())
        elif choice == '4':
            print("Running all tests...")
            asyncio.run(debug_agent_step_by_step())
            asyncio.run(test_minimal_research())
            asyncio.run(test_with_explicit_instructions())
        elif choice == '5':
            print("👋 Exiting debug session")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    try:
        main_debug()
    except KeyboardInterrupt:
        print("\n👋 Debug session interrupted")
    except Exception as e:
        print(f"\n❌ Debug session error: {e}")
        import traceback
        traceback.print_exc()

