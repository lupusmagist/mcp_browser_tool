import asyncio
from pydantic import BaseModel
from typing import Optional
from fastmcp import FastMCP
from browser_tool import BrowserTool

mcp = FastMCP(name="web_tools")

# Request models
class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 10

class NavigateRequest(BaseModel):
    url: str
    wait_for_element: Optional[str] = None
    wait_time: int = 10

class ExtractContentRequest(BaseModel):
    url: Optional[str] = None
    wait_for_element: Optional[str] = None

class SummarizeRequest(BaseModel):
    text: str
    max_tokens: int = 200

class CrawlRequest(BaseModel):
    url: str
    max_depth: int = 2

class BrowserToolRequest(BaseModel):
    action: str  # 'search', 'get_page', 'summarize'
    query: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    max_results: Optional[int] = 10
    max_tokens: Optional[int] = 200

# Global browser instance that will be shared across tool calls
_browser_tool_instance = None

async def get_browser_tool():
    """Get or create the global BrowserTool instance"""
    global _browser_tool_instance
    if _browser_tool_instance is None:
        _browser_tool_instance = BrowserTool()
    return _browser_tool_instance

async def cleanup_browser():
    """Cleanup the global browser instance"""
    global _browser_tool_instance
    if _browser_tool_instance is not None:
        await _browser_tool_instance.close()
        _browser_tool_instance = None

@mcp.tool()
async def web_search(query: str, max_results: int = 10) -> dict:
    """Perform web search using SearXNG
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing search results with title, url, and snippet
    """
    browser = await get_browser_tool()
    results = await browser.web_search(query, max_results)
    return {"results": results}

@mcp.tool()
async def navigate(url: str, wait_for_element: Optional[str] = None, wait_time: int = 10) -> dict:
    """Navigate to a URL and optionally wait for an element
    
    Args:
        url: URL to navigate to
        wait_for_element: CSS selector to wait for (optional)
        wait_time: Maximum time to wait in seconds (default: 10)
    
    Returns:
        Status message indicating navigation success
    """
    browser = await get_browser_tool()
    await browser.navigate(url, wait_for_element, wait_time)
    return {"status": "success", "message": f"Navigated to {url}"}

@mcp.tool()
async def extract_content(url: Optional[str] = None, wait_for_element: Optional[str] = None) -> dict:
    """Extract text content from a web page
    
    Args:
        url: URL to extract content from (optional, uses current page if not provided)
        wait_for_element: CSS selector to wait for before extraction (optional)
    
    Returns:
        Dictionary containing the extracted text content
    """
    browser = await get_browser_tool()
    content = await browser.extract_content(url, wait_for_element)
    return {"content": content}

@mcp.tool()
async def summarize(text: str, max_tokens: int = 200) -> dict:
    """Summarize text using a local LLM
    
    Args:
        text: Text to summarize
        max_tokens: Maximum number of tokens in the summary (default: 200)
    
    Returns:
        Dictionary containing the summary
    """
    browser = await get_browser_tool()
    summary = await browser.summarize(text, max_tokens)
    return {"summary": summary}

@mcp.tool()
async def get_page_content(url: str) -> dict:
    """Navigate to a URL and extract its full text content in one operation
    
    Args:
        url: URL to fetch and extract content from
    
    Returns:
        Dictionary containing the extracted text content
    """
    browser = await get_browser_tool()
    await browser.navigate(url)
    content = await browser.extract_content()
    return {"url": url, "content": content}

@mcp.tool()
async def close_browser() -> dict:
    """Close the browser instance and clean up resources
    
    Returns:
        Status message confirming browser closure
    """
    await cleanup_browser()
    return {"status": "success", "message": "Browser closed successfully"}

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)