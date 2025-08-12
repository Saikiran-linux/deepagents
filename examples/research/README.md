# Enhanced Deep Research Agent

This enhanced research agent is designed to conduct comprehensive, multi-faceted research and generate detailed, authoritative reports similar to professional research documents.

## Key Improvements

### 🔍 Enhanced Search Capabilities
- **Comprehensive Internet Search**: Retrieves up to 8 results with full content for detailed analysis
- **Domain-Specific Search**: Target specific authoritative sources (GitHub, official docs, academic papers)
- **Multiple Search Strategies**: Combines broad exploration with focused domain searches

### 🤖 Improved Research Methodology
- **Multi-angle Investigation**: Approaches topics from multiple perspectives
- **Structured Research Process**: Systematic coverage of core concepts, features, architecture, use cases, and comparisons
- **Authoritative Source Prioritization**: Focuses on official documentation, expert sources, and current information

### 📝 Enhanced Report Generation
- **Professional Structure**: Clear headings, logical flow, comprehensive coverage
- **Detailed Analysis**: Includes specific facts, examples, and technical details
- **Proper Citations**: Authoritative sources with proper formatting
- **Quality Assurance**: Built-in critique and revision process

### 🛠️ New Tools Added
1. **Enhanced `internet_search`**: Returns more results with full content
2. **New `search_specific_sources`**: Search within specific domains for authoritative information

## Usage

### Command Line
```bash
# Use with a specific question
python research_agent.py "What is machine learning and how does it work?"

# Use with default question (from question.txt or built-in default)
python research_agent.py

# Run file writing test
python research_agent.py --test

# Run interactive test suite
python test_research.py

# Debug file writing issues
python debug_research.py
```

### Programmatic Usage
```python
import asyncio
from research_agent import main

# Run with specific question
await main("What are the latest developments in AI safety?")

# Run with default question
await main()
```

### Question Sources (Priority Order)
1. **Command line argument**: `python research_agent.py "Your question here"`
2. **question.txt file**: Place your question in the question.txt file
3. **Default**: Falls back to built-in default question

## Research Process

The agent follows a comprehensive 4-phase research methodology:

### Phase 1: Initial Setup
- Saves the research question for reference
- Analyzes the question to identify key investigation areas
- Plans research approach by breaking down complex topics

### Phase 2: Comprehensive Research
- Conducts multiple focused research sessions covering:
  - Core concepts and definitions
  - Key features and capabilities
  - Technical architecture and implementation
  - Use cases and applications
  - Comparisons with alternatives
  - Current state and future trends
  - Best practices and examples

### Phase 3: Report Writing
- Writes detailed, well-structured reports with:
  - Professional formatting with clear sections
  - Specific facts, examples, and detailed explanations
  - Proper citations and sources section
  - Comprehensive coverage of all aspects

### Phase 4: Quality Assurance
- Uses critique agent to review for:
  - Completeness and accuracy
  - Proper structure and flow
  - Citation quality and coverage
  - Technical depth and clarity
- Conducts additional research if gaps are identified
- Revises based on feedback until high standards are met

## Output Files

After completion, you'll find:
- **`final_report.md`**: Comprehensive research report
- **`question.txt`**: Original research question for reference

## Requirements

### Essential Dependencies
```bash
pip install langgraph langchain_community tavily-python deepagents
```

### Optional Dependencies (for enhanced display)
```bash
pip install rich
```

### Environment Setup
Create a `.env` file in the project root with:
```
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # or other LLM provider keys
```

## Features

### Research Quality
- **Multi-source verification**: Uses multiple search strategies and sources
- **Depth and breadth**: Balances comprehensive coverage with detailed analysis
- **Current information**: Prioritizes recent, authoritative sources
- **Expert insights**: Provides analysis and interpretation, not just information collection

### Report Quality
- **Professional format**: Clear markdown structure with proper headings
- **Comprehensive coverage**: Addresses all major aspects of research topics
- **Authoritative sources**: Includes proper citations with source verification
- **Practical applications**: Covers real-world use cases and examples

### User Experience
- **Flexible input**: Multiple ways to specify research questions
- **Progress tracking**: Real-time display of research progress (with rich)
- **Error handling**: Graceful handling of API issues and interruptions
- **Scalable**: Handles complex topics through systematic breakdown

## Example Research Topics

The enhanced agent excels at researching:
- **Technology frameworks and tools** (e.g., "What is LangGraph?")
- **Complex technical concepts** (e.g., "How does distributed computing work?")
- **Industry trends and analysis** (e.g., "Current state of AI safety research")
- **Comparative analysis** (e.g., "Comparison of cloud platforms for ML")
- **Implementation guides** (e.g., "Best practices for microservices architecture")

## Configuration

### Research Depth
The agent is configured for comprehensive research:
- **5-8 research subtopics** for complex questions
- **Up to 8 search results** per query with full content
- **Multiple research iterations** with critique and revision
- **Parallel research agents** for efficiency

### Quality Standards
Reports meet professional standards with:
- Comprehensive coverage of all major aspects
- Specific facts, features, and examples
- Well-structured format with clear headings
- Authoritative sources with proper citations
- Technical depth balanced with accessibility

This enhanced research agent transforms simple questions into comprehensive, professional-quality research reports suitable for academic, business, or technical documentation purposes.

## Troubleshooting

### File Writing Issues
If the research agent completes but no files are created:

1. **Run the test command** to verify file writing works:
   ```bash
   python research_agent.py --test
   ```

2. **Use the debug script** for detailed diagnosis:
   ```bash
   python debug_research.py
   ```

3. **Check for errors** in the console output during execution

4. **Verify environment** has all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Common Issues
- **No TAVILY_API_KEY**: Ensure your `.env` file contains `TAVILY_API_KEY=your_key_here`
- **No LLM API key**: Ensure you have `OPENAI_API_KEY` or other model provider keys
- **Permission issues**: Check that the script has write permissions in the directory
- **Path issues**: Run the script from the `examples/research/` directory

### Debug Features
The enhanced agent includes several debugging capabilities:
- File writing verification tests
- Step-by-step execution debugging  
- Tool availability checking
- Explicit instruction testing

Use these when troubleshooting issues with report generation.
