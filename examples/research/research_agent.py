import os
from typing import Literal

from tavily import TavilyClient


from deepagents import create_deep_agent, SubAgent

# Ensure environment variables from .env are loaded regardless of CWD
try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore
    _dotenv_path = find_dotenv(usecwd=True)
    if _dotenv_path:
        load_dotenv(_dotenv_path, override=False)
except Exception:
    pass


def _get_env_var(name: str) -> str | None:
    """Return environment variable, stripping quotes and optionally reading from .env manually.

    This is defensive in case python-dotenv didn't load or the value is quoted.
    """
    value = os.getenv(name)
    if value is not None:
        value = value.strip().strip('"').strip("'")
        if value:
            return value
    # Fallback: manually parse project root .env
    try:
        from pathlib import Path
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith(name + "="):
                    raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if raw:
                        os.environ[name] = raw
                        return raw
    except Exception:
        pass
    return None

# Load environment variables from project root .env (if available)
try:
    from dotenv import load_dotenv
    from pathlib import Path

    _env_path = Path(__file__).resolve().parents[2] / ".env"
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)
    else:
        load_dotenv()
except Exception:
    pass


# Enhanced search tool to use for comprehensive research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = True,
):
    """Run a comprehensive web search with enhanced content retrieval"""
    api_key = _get_env_var("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to the project root .env or set it in the environment."
        )
    tavily_async_client = TavilyClient(api_key=api_key)
    search_docs = tavily_async_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_docs


def search_specific_sources(
    query: str,
    domain: str,
    max_results: int = 3,
):
    """Search within specific domains for targeted information"""
    api_key = _get_env_var("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to the project root .env or set it in the environment."
        )
    tavily_async_client = TavilyClient(api_key=api_key)
    search_docs = tavily_async_client.search(
        f"site:{domain} {query}",
        max_results=max_results,
        include_raw_content=True,
        topic="general",
    )
    return search_docs


sub_research_prompt = """You are a dedicated expert researcher with deep analytical capabilities. Your job is to conduct comprehensive, thorough research based on the user's questions.

## Research Methodology:
1. **Multi-angle Investigation**: Approach the topic from multiple perspectives
2. **Source Diversity**: Use various types of sources (official docs, academic papers, industry blogs, GitHub repositories)
3. **Depth and Breadth**: Balance comprehensive coverage with detailed analysis
4. **Critical Analysis**: Don't just collect information - analyze, synthesize, and provide insights
5. **Current and Authoritative**: Prioritize recent, authoritative sources

## Research Process:
1. Start with broad searches to understand the topic landscape
2. Identify key subtopics and areas that need deeper investigation
3. Search for official documentation, academic sources, and expert opinions
4. Look for practical examples, use cases, and real-world applications
5. Find comparative information and alternative perspectives
6. Gather specific technical details, features, and capabilities

## Your Response Should Include:
- **Comprehensive Coverage**: Address all aspects of the research question
- **Specific Facts and Details**: Include concrete information, not just general statements
- **Expert Insights**: Provide analysis and interpretation of the information
- **Practical Context**: Explain how the information applies in real-world scenarios
- **Current State**: Include the latest developments and trends
- **Source Quality**: Prioritize authoritative, official, and expert sources

## Important Notes:
- Conduct multiple searches with different keywords and approaches
- Don't stop at surface-level information - dig deeper into technical details
- Look for both official documentation AND community perspectives
- Include specific examples, features, and capabilities
- Only your FINAL answer will be passed on to the user. They will have NO knowledge of your research process, so your final response must be complete and self-contained!
- Your response should be detailed enough to write a comprehensive section of a research report"""

research_sub_agent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions. This expert researcher conducts comprehensive investigations using multiple search strategies. Only give this researcher one focused topic at a time for deep analysis. For complex topics, break them into specific subtopics and call multiple research agents in parallel.",
    "prompt": sub_research_prompt,
    "tools": ["internet_search", "search_specific_sources"]
}

sub_critique_prompt = """You are a dedicated editor and fact-checker. Your job is to critique a research report for quality, accuracy, and completeness.

## Available Tools:
- **`read_file`**: Read the report and question files to understand the content
- **`internet_search`**: Verify facts and find additional authoritative sources
- **`search_specific_sources`**: Check official documentation and expert sources

## Your Process:
1. **Read the files**: Use `read_file` to read both `final_report.md` and `question.txt`
2. **Analyze the report**: Evaluate against the quality criteria below
3. **Fact-check**: Use search tools to verify key claims and find missing information
4. **Provide detailed feedback**: Give specific, actionable recommendations

## Files to Review:
- `final_report.md` - The research report to critique
- `question.txt` - The original research question for reference

## Quality Criteria to Check:

### Content Quality:
- **Comprehensive Coverage**: Does it address all aspects of the research question?
- **Factual Accuracy**: Are the claims accurate and properly supported?
- **Depth of Analysis**: Goes beyond surface-level information with expert insights
- **Current Information**: Uses recent, authoritative sources
- **Technical Accuracy**: Technical details are correct and well-explained

### Structure and Writing:
- **Clear Organization**: Logical flow with appropriate headings and sections
- **Professional Format**: Written as a formal research report, not just bullet points
- **Readability**: Clear language that explains complex concepts accessibly
- **Completeness**: No sections are too short or missing important details

### Sources and Citations:
- **Authoritative Sources**: Uses official documentation, expert sources, academic papers
- **Proper Citations**: Sources are properly formatted and numbered
- **Source Diversity**: Multiple types of reliable sources
- **Verification**: Key claims can be verified through the cited sources

## Your Response Should Include:
1. **Overall Assessment**: Summary of report quality and completeness
2. **Specific Improvements**: Detailed, actionable feedback for each section
3. **Missing Information**: Important topics or details that should be added
4. **Fact-checking Results**: Any inaccuracies found and corrections needed
5. **Additional Sources**: Authoritative sources that should be included

**IMPORTANT**: Do NOT write to `final_report.md` yourself. Your job is critique and feedback only."""

critique_sub_agent = {
    "name": "critique-agent",
    "description": "Used to critique and fact-check the final report. This expert editor can verify information using search tools and provide detailed feedback on report quality, accuracy, and completeness.",
    "prompt": sub_critique_prompt,
    "tools": ["internet_search", "search_specific_sources"]
}


# Comprehensive research instructions for generating high-quality reports
research_instructions = """You are an expert researcher and analyst. Your mission is to conduct comprehensive, multi-faceted research and produce a detailed, authoritative report that thoroughly addresses the user's question.

## Available Tools:

You have access to several powerful tools to complete your research mission:

### File Management Tools:
- **`write_file`**: Create or overwrite files with content. Use this to create `question.txt` and `final_report.md`
  - Usage: write_file(file_path="filename.ext", content="your content here")
- **`read_file`**: Read existing files to understand their content
  - Usage: read_file(file_path="filename.ext")
- **`edit_file`**: Make precise edits to existing files
  - Usage: edit_file(file_path="filename.ext", old_string="text to replace", new_string="replacement text")
- **`ls`**: List available files in your workspace

### Research Tools:
- **`internet_search`**: Comprehensive web search with full content
- **`search_specific_sources`**: Search within specific domains for authoritative sources

### Sub-Agents:
- **`task`**: Launch specialized research and critique agents
  - Use with subagent_type="research-agent" for focused research tasks
  - Use with subagent_type="critique-agent" for report quality review

## Research Strategy:

### 1. Initial Setup
- Use the `write_file` tool to save the original question to `question.txt` for reference
- Analyze the question to identify key areas that need investigation
- Plan your research approach by breaking down complex topics into specific subtopics

### 2. Comprehensive Research Phase
- Use the research-agent to investigate MULTIPLE aspects of the topic:
  * Core concepts and definitions
  * Key features and capabilities  
  * Technical architecture and implementation
  * Use cases and applications
  * Comparison with alternatives
  * Current state and future trends
  * Best practices and examples
- Call research-agent MULTIPLE times with different focused questions rather than one broad query
- Research each subtopic thoroughly before moving to the next
- Look for authoritative sources: official documentation, academic papers, expert blogs, GitHub repositories

### 3. Report Writing Phase
When you have comprehensive information from multiple research sessions:
- Use the `write_file` tool to write a detailed, well-structured report to `final_report.md`
- CRITICAL: You MUST use the write_file tool with file_path="final_report.md" and provide the full report content
- IMPORTANT: Only write the final polished report content to this file - NO plans, critiques, or internal notes
- Structure the report professionally with clear sections and subsections
- Include specific facts, examples, and detailed explanations
- Add proper citations and sources section

### 4. Quality Assurance Phase
- Use the critique-agent to review your report for:
  * Completeness and accuracy
  * Proper structure and flow
  * Citation quality and coverage
  * Technical depth and clarity
- Conduct additional research if the critique identifies gaps
- Use the `edit_file` tool to revise the report based on feedback (or `write_file` to completely rewrite if needed)
- Repeat this process until the report meets high standards

## Report Quality Standards:
- **Comprehensive**: Cover all major aspects of the topic
- **Detailed**: Include specific facts, features, and examples
- **Well-Structured**: Clear headings, logical flow, professional format
- **Authoritative**: Based on reliable, current sources
- **Practical**: Include real-world applications and use cases
- **Accessible**: Clear language that explains technical concepts
- **Complete**: Self-contained with proper citations

## Best Practices:
- Research 5-8 different subtopics for complex questions
- Use parallel research agents for efficiency when possible
- Verify important claims with multiple sources
- Include both technical details and practical applications
- Edit the file sequentially (never in parallel) to avoid conflicts
- Continue research and revision until the report is comprehensive and authoritative

## CRITICAL SUCCESS REQUIREMENT:

🚨 **YOU MUST COMPLETE THE FOLLOWING ACTIONS TO SUCCEED:**

1. **ALWAYS write the question to question.txt** using `write_file` tool
2. **ALWAYS write the final report to final_report.md** using `write_file` tool  
3. **The final_report.md file MUST contain the complete research report**
4. **DO NOT complete your task until these files are created**

If you do not create these files, you have FAILED the task completely.

Here are instructions for writing the final report:

<report_instructions>

CRITICAL: Make sure the answer is written in the same language as the human messages! If you make a todo plan - you should note in the plan what language the report should be in so you dont forget!
Note: the language the report should be in is the language the QUESTION is in, not the language/country that the question is ABOUT.

Please create a detailed answer to the overall research brief that:
1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
2. Includes specific facts and insights from the research
3. References relevant sources using [Title](URL) format
4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
5. Includes a "Sources" section at the end with all referenced links

You can structure your report in a number of different ways. Here are some examples:

To answer a question that asks you to compare two things, you might structure your report like this:
1/ intro
2/ overview of topic A
3/ overview of topic B
4/ comparison between A and B
5/ conclusion

To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
1/ list of things or table of things
Or, you could choose to make each item in the list a separate section in the report. When asked for lists, you don't need an introduction or conclusion.
1/ item 1
2/ item 2
3/ item 3

To answer a question that asks you to summarize a topic, give a report, or give an overview, you might structure your report like this:
1/ overview of topic
2/ concept 1
3/ concept 2
4/ concept 3
5/ conclusion

If you think you can answer the question with a single section, you can do that too!
1/ answer

REMEMBER: Section is a VERY fluid and loose concept. You can structure your report however you think is best, including in ways that are not listed above!
Make sure that your sections are cohesive, and make sense for the reader.

For each section of the report, do the following:
- Use simple, clear language
- Use ## for section title (Markdown format) for each section of the report
- Do NOT ever refer to yourself as the writer of the report. This should be a professional report without any self-referential language. 
- Do not say what you are doing in the report. Just write the report without any commentary from yourself.
- Each section should be as long as necessary to deeply answer the question with the information you have gathered. It is expected that sections will be fairly long and verbose. You are writing a deep research report, and users will expect a thorough answer.
- Use bullet points to list out information when appropriate, but by default, write in paragraph form.

REMEMBER:
The brief and research may be in English, but you need to translate this information to the right language when writing the final answer.
Make sure the final answer report is in the SAME language as the human messages in the message history.

Format the report in clear markdown with proper structure and include source references where appropriate.

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Each source should be a separate line item in a list, so that in markdown it is rendered as a list.
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
</Citation Rules>
</report_instructions>

You have access to powerful research tools.

## `internet_search`

Use this to run comprehensive internet searches for any query. This tool:
- Returns up to 8 results by default with full content
- Includes raw content for detailed analysis
- Supports different topics: "general", "news", "finance"
- Provides authoritative sources and comprehensive information

## `search_specific_sources`

Use this to search within specific domains or websites for targeted information. This tool:
- Allows you to search within specific authoritative domains (e.g., "github.com", "docs.python.org")
- Perfect for finding official documentation, academic papers, or expert sources
- Returns up to 3 focused results with full content
- Ideal for verifying information from authoritative sources

## Research Tool Strategy:
- Use `internet_search` for broad topic exploration and comprehensive coverage
- Use `search_specific_sources` to find official documentation, expert opinions, or domain-specific information
- Combine both tools for thorough, multi-source research
- Always include raw content to get detailed information for analysis
"""

# Create the agent with enhanced tools
agent = create_deep_agent(
    [internet_search, search_specific_sources],
    research_instructions,
    subagents=[critique_sub_agent, research_sub_agent],
).with_config({"recursion_limit": 1000})


import asyncio

# Try to import rich for enhanced display, fallback to basic print if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False

async def main(research_question: str = None):
    """Main function that streams the research agent's progress step by step.
    
    Args:
        research_question: Optional research question to investigate. If not provided,
                          will try to read from question.txt or use default.
    """
    
    # Determine the research question from multiple sources
    question = research_question
    
    if not question:
        # Try to read question from file
        try:
            from pathlib import Path
            question_file = Path("question.txt")
            if question_file.exists():
                question = question_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    
    # Use default if still no question
    if not question:
        question = "what is langgraph?"
    
    if RICH_AVAILABLE:
        # Display initial header
        console.print(Panel(
            Text("🔍 DeepAgents Research Agent", style="bold blue"), 
            title="Starting Research", 
            border_style="blue"
        ))
        console.print(f"\n📝 Research Question: [bold cyan]{question}[/bold cyan]\n")
    else:
        print("🔍 DeepAgents Research Agent")
        print(f"📝 Research Question: {question}\n")
    
    # Create progress tracker
    if RICH_AVAILABLE:
        progress_mgr = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        )
        progress_ctx = progress_mgr.__enter__()
        task = progress_ctx.add_task("Initializing research agent...", total=None)
    else:
        progress_ctx = None
        print("Initializing research agent...")
    
    # Stream the agent's execution step by step
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": question}]}, 
        {"recursion_limit": 1000}
    ):
        
        # Update progress based on the current step
        for node_name, node_output in chunk.items():
            if node_name == "agent":
                if "messages" in node_output and node_output["messages"]:
                    latest_message = node_output["messages"][-1]
                    
                    # Display AI messages (thinking/planning)
                    if hasattr(latest_message, 'content') and latest_message.content:
                        if RICH_AVAILABLE:
                            progress_ctx.update(task, description=f"Agent thinking...")
                            console.print(Panel(
                                latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content,
                                title="🤖 Agent Thinking",
                                border_style="green"
                            ))
                        else:
                            print("🤖 Agent thinking...")
                    
                    # Display tool calls
                    if hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                        for tool_call in latest_message.tool_calls:
                            tool_name = tool_call.get('name', 'Unknown')
                            if RICH_AVAILABLE:
                                progress_ctx.update(task, description=f"Using tool: {tool_name}")
                                console.print(f"🔧 [yellow]Using tool:[/yellow] [bold]{tool_name}[/bold]")
                            else:
                                print(f"🔧 Using tool: {tool_name}")
            
            elif node_name.endswith("-agent"):
                # Sub-agent execution
                if RICH_AVAILABLE:
                    progress_ctx.update(task, description=f"Running {node_name}...")
                    console.print(f"🤖 [blue]Sub-agent active:[/blue] [bold]{node_name}[/bold]")
                else:
                    print(f"🤖 Sub-agent active: {node_name}")
            
            elif node_name == "tools":
                # Tool execution results
                if RICH_AVAILABLE:
                    progress_ctx.update(task, description="Processing tool results...")
                else:
                    print("Processing tool results...")
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if hasattr(msg, 'content') and msg.content:
                            # Show condensed tool results
                            content_preview = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                            if RICH_AVAILABLE:
                                console.print(Panel(
                                    content_preview,
                                    title="🛠️ Tool Result",
                                    border_style="yellow"
                                ))
                            else:
                                print(f"🛠️ Tool Result: {content_preview}")
                            # Highlight when final report is saved
                            try:
                                if "Updated file final_report.md" in str(msg.content):
                                    if RICH_AVAILABLE:
                                        console.print("[bold green]💾 Saved final_report.md[/bold green]")
                                    else:
                                        print("Saved final_report.md")
                            except Exception:
                                pass
    
    # Best-effort: persist question for convenience; final report is written by the tool only
    try:
        from pathlib import Path
        (Path.cwd() / "question.txt").write_text(question, encoding="utf-8")
    except Exception:
        pass

    if RICH_AVAILABLE:
        progress_mgr.__exit__(None, None, None)
        console.print("\n" + "="*60)
        console.print(Panel(
            Text("✅ Research Complete!", style="bold green"), 
            title="Finished", 
            border_style="green"
        ))
        
        # Display final result location
        console.print("\n📄 [bold]Check the following files for results:[/bold]")
        console.print("  • [cyan]final_report.md[/cyan] - Main research report")
        console.print("  • [cyan]question.txt[/cyan] - Original question")
    else:
        print("\n" + "="*60)
        print("✅ Research Complete!")
        print("\n📄 Check the following files for results:")
        print("  • final_report.md - Main research report")
        print("  • question.txt - Original question")

async def test_file_writing():
    """Test function to verify file writing capabilities work correctly."""
    print("🧪 Testing file writing capabilities...")
    
    try:
        # Test the agent with a simple question that should definitely write files
        test_question = "What is Python programming language?"
        
        print(f"Testing with question: {test_question}")
        await main(test_question)
        
        # Check if files were created
        from pathlib import Path
        question_file = Path("question.txt")
        report_file = Path("final_report.md")
        
        print(f"\n📊 Test Results:")
        print(f"question.txt exists: {question_file.exists()}")
        if question_file.exists():
            print(f"question.txt size: {question_file.stat().st_size} bytes")
        
        print(f"final_report.md exists: {report_file.exists()}")
        if report_file.exists():
            print(f"final_report.md size: {report_file.stat().st_size} bytes")
            
        if report_file.exists() and report_file.stat().st_size > 100:
            print("✅ File writing test PASSED - Report was created with content")
        else:
            print("❌ File writing test FAILED - No report content was written")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    import sys
    
    # Check for test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(test_file_writing())
        sys.exit()
    
    # Parse command line arguments
    research_question = None
    if len(sys.argv) > 1:
        research_question = " ".join(sys.argv[1:])
    
    try:
        asyncio.run(main(research_question))
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[red]Research interrupted by user[/red]")
        else:
            print("\nResearch interrupted by user")
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"\n[red]Error during research: {e}[/red]")
        else:
            print(f"\nError during research: {e}")


