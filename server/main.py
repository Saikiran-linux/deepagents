import os
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Ensure project src is importable when running server directly
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
EXAMPLES_DIR = ROOT_DIR / "examples"
EXAMPLES_RESEARCH_DIR = EXAMPLES_DIR / "research"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(EXAMPLES_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_RESEARCH_DIR))


try:
    # Load environment from project root .env if present
    from dotenv import load_dotenv  # type: ignore

    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        load_dotenv(override=False)
except Exception:
    pass


app = FastAPI(title="DeepAgents Server", version="0.1.0")

# Allow local dev by default
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    agent_id: str
    prompt: str
    # Optional: future fields
    recursion_limit: int | None = 1000


def _import_research_agent():
    """Import and return the research agent.

    Returns a tuple: (agent, module)
    """
    try:
        # Try to import the simplified research agent first
        from . import simple_research_agent as research_mod  # type: ignore
        research_agent = getattr(research_mod, "simple_research_agent")
        return research_agent, research_mod
    except Exception:
        try:
            # Fallback to the original research agent from examples
            import research_agent as research_mod  # type: ignore
            research_agent = getattr(research_mod, "agent")
            return research_agent, research_mod
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                f"Failed to import research agent. Ensure package is installed (`pip install -e .`) and examples path is available. Error: {exc}"
            ) from exc


@app.get("/api/agents")
def list_agents() -> Dict[str, Any]:
    """List available agents for selection in the UI."""
    # For now only research is available; this can be extended later
    return {
        "agents": [
            {"id": "research", "name": "Research Agent", "description": "Deep research with web search and report writing"}
        ]
    }


@app.post("/api/agent/run")
async def run_agent(req: RunRequest) -> Dict[str, Any]:
    if req.agent_id != "research":
        raise HTTPException(status_code=400, detail=f"Unknown agent_id: {req.agent_id}")

    # Validate env (Tavily API is required by the example agent tools)
    tavily_key = os.getenv("TAVILY_API_KEY")
    print(f"DEBUG: TAVILY_API_KEY found: {bool(tavily_key)}")  # Debug line
    if not tavily_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "TAVILY_API_KEY is not set. Add it to a .env at project root or set environment variable."
            ),
        )

    research_agent, _ = _import_research_agent()

    # Run the agent and capture virtual file outputs
    try:
        print(f"DEBUG: Invoking research agent with prompt: {req.prompt[:50]}...")
        result = await research_agent.ainvoke(
            {"messages": [{"role": "user", "content": req.prompt}]},
            {"recursion_limit": req.recursion_limit or 1000},
        )
        print(f"DEBUG: Agent result type: {type(result)}")
        print(f"DEBUG: Agent result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print(f"DEBUG: Files in result: {result.get('files', {}) if isinstance(result, dict) else 'No files'}")
        print(f"DEBUG: Messages in result: {len(result.get('messages', [])) if isinstance(result, dict) else 'No messages'}")
        if isinstance(result, dict) and 'messages' in result:
            for i, msg in enumerate(result['messages']):
                if hasattr(msg, 'content'):
                    content = msg.content
                    print(f"DEBUG: Message {i} content preview: {content[:100] if content else 'None'}...")
                elif isinstance(msg, dict) and 'content' in msg:
                    content = msg['content']
                    print(f"DEBUG: Message {i} content preview: {content[:100] if content else 'None'}...")
    except Exception as exc:
        print(f"DEBUG: Agent error: {exc}")
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    files = result.get("files", {}) if isinstance(result, dict) else {}
    report_content = files.get("final_report.md")
    
    # If we have a report file, ensure it has proper reference links
    if report_content and isinstance(report_content, str):
        # Check if the report already has a Sources section
        if "## Sources" not in report_content and "### Sources" not in report_content:
            # Look for any URLs in the content and create a Sources section
            url_pattern = r'https?://[^\s\)]+'
            urls = re.findall(url_pattern, report_content)
            if urls:
                # Remove duplicates and format as numbered list
                unique_urls = list(dict.fromkeys(urls))  # Preserve order while removing duplicates
                sources_section = "\n\n## Sources\n\n"
                for i, url in enumerate(unique_urls, 1):
                    # Try to extract domain name for better readability
                    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                    domain = domain_match.group(1) if domain_match else url
                    sources_section += f"{i}. [{domain}]({url})\n"
                report_content += sources_section

    # Extract all messages to capture both commentary and final report
    messages = result.get("messages", []) if isinstance(result, dict) else []
    last_assistant = None
    commentary_steps = []
    
    print(f"DEBUG: Processing {len(messages)} messages")
    
    if messages:
        for i, msg in enumerate(messages):
            print(f"DEBUG: Message {i} type: {type(msg)}")
            if isinstance(msg, dict):
                print(f"DEBUG: Message {i} keys: {list(msg.keys())}")
                print(f"DEBUG: Message {i} role: {msg.get('role')}")
                print(f"DEBUG: Message {i} content preview: {str(msg.get('content', ''))[:100]}...")
            else:
                print(f"DEBUG: Message {i} attributes: {[attr for attr in dir(msg) if not attr.startswith('_')]}")
                print(f"DEBUG: Message {i} role: {getattr(msg, 'role', 'N/A')}")
                print(f"DEBUG: Message {i} type: {getattr(msg, 'type', 'N/A')}")
                print(f"DEBUG: Message {i} content preview: {str(getattr(msg, 'content', ''))[:100]}...")
        
        # Find the last message with actual content
        for msg in reversed(messages):
            msg_content = None
            if isinstance(msg, dict):
                # Handle dict-like message
                if msg.get("role") == "assistant":
                    msg_content = msg.get("content")
            else:
                # Handle LangChain message objects
                if getattr(msg, "role", None) == "assistant" or getattr(msg, "type", None) == "ai":
                    msg_content = getattr(msg, "content", None)
            
            if msg_content:
                last_assistant = msg_content
                print(f"DEBUG: Found last_assistant with content length: {len(msg_content)}")
                break
    
    # Parse commentary and clean content
    clean_report = None
    if last_assistant:
        # Extract commentary sections marked with various commentary tags
        import re
        
        # Debug logging
        print(f"DEBUG: Processing message of length: {len(last_assistant)}")
        print(f"DEBUG: Message preview: {last_assistant[:200]}...")
        
        # Check for commentary patterns before processing
        commentary_indicators = [
            '<|channel|>commentary<|message|>',
            'commentary',
            '<|end|>',
            '<|channel|>',
            '<|message|>'
        ]
        found_indicators = [indicator for indicator in commentary_indicators if indicator in last_assistant]
        print(f"DEBUG: Found commentary indicators: {found_indicators}")
        
        # Use a single, comprehensive pattern to extract all commentary
        commentary_pattern = r'<\|channel\|>commentary<\|message\|>(.*?)(?=<\|channel\||<\|end\||$)'
        commentary_matches = re.findall(commentary_pattern, last_assistant, re.DOTALL)
        print(f"DEBUG: Found {len(commentary_matches)} commentary sections")
        
        # Process each commentary section
        for i, comment in enumerate(commentary_matches):
            comment = comment.strip()
            print(f"DEBUG: Processing commentary {i+1}, length: {len(comment)}")
            if comment:
                # Convert commentary into thinking steps
                if "plan to synthesize a report covering:" in comment:
                    commentary_steps.append({
                        "text": "📋 Planning comprehensive research report structure",
                        "tools": ["Research Planner", "Content Organizer"]
                    })
                    # Extract bullet points as individual steps
                    lines = comment.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('•') or line.startswith('-'):
                            clean_line = line.replace('•', '').replace('-', '').strip()
                            if clean_line:
                                commentary_steps.append({
                                    "text": f"🔍 Researching: {clean_line}",
                                    "tools": ["Research Agent", "Source Analyzer"]
                                })
                elif "1000+ words" in comment:
                    commentary_steps.append({
                        "text": "📏 Ensuring comprehensive coverage (1000+ words)",
                        "tools": ["Content Validator", "Quality Checker"]
                    })
                elif "citations" in comment.lower():
                    commentary_steps.append({
                        "text": "📖 Adding proper citations and references",
                        "tools": ["Citation Manager", "Source Validator"]
                    })
                elif "search results" in comment.lower():
                    commentary_steps.append({
                        "text": "🔍 Analyzing search results and gathering information",
                        "tools": ["Search Analyzer", "Content Gatherer"]
                    })
                elif "orchestrate" in comment.lower():
                    commentary_steps.append({
                        "text": "🔄 Orchestrating research process and document analysis",
                        "tools": ["Process Orchestrator", "Document Manager"]
                    })
                else:
                    # Generic commentary step
                    preview = comment[:100] + "..." if len(comment) > 100 else comment
                    commentary_steps.append({
                        "text": f"💭 {preview}",
                        "tools": ["Research Agent", "Content Processor"]
                    })
        
        # More aggressive commentary removal - remove ALL commentary tags and content
        clean_content = last_assistant
        
        # Remove all commentary sections completely - multiple passes to ensure complete removal
        # First pass: remove commentary sections with channel tags
        clean_content = re.sub(r'<\|channel\|>commentary<\|message\|>.*?(?=<\|channel\||<\|end\||$)', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'<\|channel\|>commentary<\|message\|>.*?(?=<\|end\||$)', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'<\|channel\|>commentary<\|message\|>.*$', '', clean_content, flags=re.DOTALL)
        
        # Second pass: remove any remaining commentary content without proper tags
        clean_content = re.sub(r'commentary.*?message', '', clean_content, flags=re.IGNORECASE | re.DOTALL)
        clean_content = re.sub(r'commentary.*?end', '', clean_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Third pass: remove all remaining channel and message tags
        clean_content = re.sub(r'<\|channel\|>.*?<\|message\|>', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'<\|end\|>', '', clean_content)  # Remove end tags
        clean_content = re.sub(r'<\|.*?\|>', '', clean_content)  # Remove any remaining channel tags
        
        # Fourth pass: remove any remaining commentary artifacts and clean up whitespace
        clean_content = re.sub(r'commentary.*?message', '', clean_content, flags=re.IGNORECASE | re.DOTALL)
        clean_content = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_content)  # Remove excessive blank lines
        clean_content = re.sub(r'^\s+', '', clean_content, flags=re.MULTILINE)  # Remove leading whitespace from lines
        
        # Ensure proper citation formatting
        clean_content = re.sub(r'### Sources?', '## Sources', clean_content, flags=re.IGNORECASE)
        clean_content = re.sub(r'### Citations?', '## Sources', clean_content, flags=re.IGNORECASE)
        clean_content = re.sub(r'### References?', '## Sources', clean_content, flags=re.IGNORECASE)
        
        clean_content = clean_content.strip()
        
        print(f"DEBUG: Cleaned content length: {len(clean_content)}")
        print(f"DEBUG: Cleaned content preview: {clean_content[:200]}...")
        
        # Final check for any remaining commentary artifacts
        remaining_commentary = re.search(r'commentary|channel|message|end', clean_content, re.IGNORECASE)
        if remaining_commentary:
            print(f"DEBUG: WARNING - Still found commentary artifacts: {remaining_commentary.group()}")
            # One more aggressive cleanup
            clean_content = re.sub(r'.*?commentary.*?message.*?end.*', '', clean_content, flags=re.IGNORECASE | re.DOTALL)
            clean_content = re.sub(r'commentary.*?message.*?end', '', clean_content, flags=re.IGNORECASE | re.DOTALL)
            clean_content = clean_content.strip()
            print(f"DEBUG: After final cleanup, length: {len(clean_content)}")
        
        # Use the cleaned content as the report
        if clean_content and len(clean_content) > 100:
            clean_report = clean_content

    # If no report file was created, but we have a substantial cleaned message,
    # and it looks like a research report, use it as the report content
    if not report_content and clean_report and len(clean_report) > 500:
        # Check if the cleaned message looks like a research report
        if any(indicator in clean_report for indicator in ["##", "###", "**", "Sources", "Citation", "References"]):
            # Ensure proper markdown formatting for citations
            if "## Sources" not in clean_report and "### Sources" not in clean_report:
                # Look for any citation-like content and format it properly
                citation_match = re.search(r'(\d+\.\s*.*?https?://[^\s]+)', clean_report, re.DOTALL)
                if citation_match:
                    # Add proper Sources section
                    clean_report += "\n\n## Sources\n\n" + citation_match.group(1)
                else:
                    # Look for any URLs in the content and create a Sources section
                    url_pattern = r'https?://[^\s\)]+'
                    urls = re.findall(url_pattern, clean_report)
                    if urls:
                        # Remove duplicates and format as numbered list
                        unique_urls = list(dict.fromkeys(urls))  # Preserve order while removing duplicates
                        sources_section = "\n\n## Sources\n\n"
                        for i, url in enumerate(unique_urls, 1):
                            # Try to extract domain name for better readability
                            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                            domain = domain_match.group(1) if domain_match else url
                            sources_section += f"{i}. [{domain}]({url})\n"
                        clean_report += sources_section
            
            report_content = clean_report

    # Final check: ensure the report has proper formatting and sources
    if report_content and isinstance(report_content, str):
        # Ensure proper markdown structure
        if not report_content.startswith('#'):
            # If no headers, add a main title
            report_content = f"# Research Report\n\n{report_content}"
        
        # Ensure Sources section is at the bottom and properly formatted
        if "## Sources" in report_content:
            # Move Sources section to the very end if it's not already there
            sources_match = re.search(r'(## Sources.*)', report_content, re.DOTALL)
            if sources_match:
                sources_section = sources_match.group(1)
                # Remove the sources section from its current location
                report_content = re.sub(r'## Sources.*', '', report_content, flags=re.DOTALL)
                # Add it back at the end
                report_content = report_content.strip() + "\n\n" + sources_section
    
    return {
        "agent_id": req.agent_id,
        "report": report_content,
        "assistant_message": "Research report completed successfully." if report_content else last_assistant,
        "thinking_steps": commentary_steps,
        "files": {k: (v if isinstance(v, str) else str(v)) for k, v in files.items()},
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "1") == "1"

    # Use import string when reload is enabled to avoid uvicorn warning and enable auto-reload
    if reload_enabled:
        uvicorn.run(
            "server.main:app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
        )


