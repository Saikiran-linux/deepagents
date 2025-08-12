#!/usr/bin/env python3
"""
Test script for the enhanced deep research agent.

This script demonstrates how to use the research agent programmatically
with different research questions.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path to import research_agent
sys.path.insert(0, str(Path(__file__).parent))

from research_agent import main

async def test_research_questions():
    """Test the research agent with various questions."""
    
    test_questions = [
        "What is artificial intelligence and how is it being used in healthcare?",
        "What are the latest developments in quantum computing?",
        "How do large language models work and what are their applications?",
        "What is blockchain technology and what are its real-world use cases?",
        "What is edge computing and how does it differ from cloud computing?"
    ]
    
    print("🧪 Enhanced Deep Research Agent Test Suite")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📋 Test {i}: {question}")
        print("-" * 30)
        
        user_input = input(f"Run this test? (y/N): ").strip().lower()
        if user_input == 'y':
            print(f"\n🔍 Starting research on: {question}")
            try:
                await main(question)
                print(f"\n✅ Completed research on: {question}")
                print("📄 Check final_report.md for the results")
                
                # Ask if user wants to continue
                continue_input = input("\nContinue to next test? (y/N): ").strip().lower()
                if continue_input != 'y':
                    break
            except KeyboardInterrupt:
                print("\n⏹️ Research interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error during research: {e}")
                continue
        else:
            print("⏭️ Skipping this test")
    
    print("\n🏁 Test suite completed!")

async def demo_single_question():
    """Demo with a single, interesting research question."""
    
    demo_question = "What is the current state of AI safety research and what are the main challenges?"
    
    print("🎯 Deep Research Agent Demo")
    print("=" * 40)
    print(f"\n📋 Research Question: {demo_question}")
    print("\nThis demo will show the enhanced research agent in action.")
    print("The agent will:")
    print("  • Conduct comprehensive multi-source research")
    print("  • Use multiple search strategies")
    print("  • Generate a professional research report")
    print("  • Include proper citations and sources")
    
    user_input = input("\nStart the demo? (y/N): ").strip().lower()
    if user_input == 'y':
        print(f"\n🚀 Starting comprehensive research...")
        try:
            await main(demo_question)
            print(f"\n🎉 Demo completed successfully!")
            print("📊 Results:")
            print("  • final_report.md - Comprehensive research report")
            print("  • question.txt - Original research question")
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during demo: {e}")
    else:
        print("👋 Demo cancelled")

def main_menu():
    """Main menu for test options."""
    
    print("🔬 Enhanced Deep Research Agent Testing")
    print("=" * 45)
    print("\nChoose an option:")
    print("1. Run demo with sample question")
    print("2. Run test suite with multiple questions")
    print("3. Custom research question")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            asyncio.run(demo_single_question())
            break
        elif choice == '2':
            asyncio.run(test_research_questions())
            break
        elif choice == '3':
            custom_question = input("Enter your research question: ").strip()
            if custom_question:
                print(f"\n🔍 Researching: {custom_question}")
                asyncio.run(main(custom_question))
            else:
                print("❌ No question provided")
            break
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

