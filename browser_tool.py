import os
import time
import urllib.parse
from llama_cpp import Llama
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserTool:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self._initializing = False
        
        # Initialize Llama model from .env
        model_path = os.getenv("LLM")
        if model_path:
            # Strip quotes if present (common in .env files)
            model_path = model_path.strip('"\'')
            if os.path.exists(model_path):
                try:
                    logger.info(f"Loading LLM model from: {model_path}")
                    self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)
                    logger.info("LLM model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load LLM model: {str(e)}")
                    self.llm = None
        else:
            logger.warning("LLM not configured. Set LLM environment variable to enable summarization.")
            self.llm = None

    async def _setup_browser(self):
        """Initialize playwright, browser, and page if not already initialized"""
        if self._initializing:
            # Prevent concurrent initialization
            return
        
        try:
            self._initializing = True
            
            if self.playwright is None:
                logger.info("Starting Playwright...")
                self.playwright = await async_playwright().start()
                
            if self.browser is None:
                logger.info("Launching browser...")
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
            if self.page is None:
                logger.info("Creating new page...")
                # Create context with proper settings to avoid bot detection
                context = await self.browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    },
                    java_script_enabled=True,
                    bypass_csp=True,
                    ignore_https_errors=True
                )
                
                self.page = await context.new_page()
                
                # Additional anti-detection measures
                await self.page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
            logger.info("Browser setup complete")
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            raise Exception(f"Failed to initialize browser: {str(e)}")
        finally:
            self._initializing = False

    async def web_search(self, query: str, max_results: int = 10):
        """Search using SearXNG instance"""
        await self._setup_browser()
        
        # Use SearXNG API endpoint
        searxng_url = os.getenv("SEARXNG_URL", "http://192.168.77.8:8888")
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"{searxng_url}/search?q={encoded_query}&format=json"
        
        logger.info(f"Searching for: {query}")
        logger.info(f"SearXNG URL: {search_url}")
        
        try:
            # Navigate to the search API endpoint
            response = await self.page.goto(search_url, wait_until="networkidle")
            
            if response and response.status == 200:
                # Get the JSON response
                content = await self.page.content()
                
                # Extract JSON from the page
                soup = BeautifulSoup(content, 'html.parser')
                pre_tag = soup.find('pre')
                
                if pre_tag:
                    import json
                    json_text = pre_tag.get_text()
                    data = json.loads(json_text)
                    
                    results = []
                    search_results = data.get('results', [])
                    
                    for result in search_results[:max_results]:
                        title = result.get('title', '')
                        url = result.get('url', '')
                        content_snippet = result.get('content', '')
                        
                        if title and url:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": content_snippet
                            })
                            logger.info(f"Found result: {title[:50]}...")
                    
                    logger.info(f"Total results found: {len(results)}")
                    return results
            
            logger.warning(f"Failed to get results from SearXNG, status: {response.status if response else 'None'}")
            return []
            
        except Exception as e:
            logger.error(f"SearXNG search error: {str(e)}")
            return []

    async def navigate(self, url: str, wait_for_element: Optional[str] = None, wait_time: int = 10):
        """Navigate to a URL and optionally wait for a specific element"""
        await self._setup_browser()
        
        logger.info(f"Navigating to: {url}")
        
        try:
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            if response is None:
                raise Exception(f"Failed to navigate to {url} - no response received")
            
            # Check response status if available (defensive check for testing/mocking)
            if hasattr(response, 'status') and isinstance(response.status, int):
                if response.status >= 400:
                    logger.warning(f"Navigation returned status {response.status} for {url}")
            
            if wait_for_element:
                try:
                    await self.page.wait_for_selector(wait_for_element, timeout=wait_time * 1000)
                    logger.info(f"Successfully found element: {wait_for_element}")
                except Exception as e:
                    raise Exception(f"Element '{wait_for_element}' not found on page after {wait_time}s: {str(e)}")
            
            logger.info(f"Successfully navigated to {url}")
        except Exception as e:
            logger.error(f"Navigation error for {url}: {str(e)}")
            raise Exception(f"Failed to navigate to {url}: {str(e)}")

    async def extract_content(self, url: Optional[str] = None, wait_for_element: Optional[str] = None):
        """Extract text content from a web page, removing scripts and styles"""
        await self._setup_browser()
        
        if url:
            await self.navigate(url, wait_for_element)
        
        if self.page is None:
            raise Exception("No page loaded. Navigate to a URL first.")
        
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        clean_text = ' '.join(text.split())
        
        logger.info(f"Extracted {len(clean_text)} characters of content")
        return clean_text

    async def summarize(self, text: str, max_tokens: int = 200):
        """Summarize text using the configured LLM model"""
        if not self.llm:
            raise Exception("LLM not configured. Set LLM environment variable with path to model file.")

        # Truncate text if too long (keep first ~4000 chars to fit in context)
        if len(text) > 4000:
            text = text[:4000] + "..."
            logger.warning("Text truncated to fit context window")

        prompt = f"Summarize the following text concisely:\n\n{text}\n\nSummary:"
        
        try:
            # Run LLM in a thread pool to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                lambda: self.llm(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stop=["\n\n"],
                    echo=False
                )
            )
            summary = output["choices"][0]["text"].strip()
            logger.info(f"Generated summary of {len(summary)} characters")
            return summary
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def close(self):
        """Close browser and cleanup resources"""
        logger.info("Closing browser...")
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
                
            if self.browser:
                await self.browser.close()
                self.browser = None
                
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")
            # Force reset even if cleanup fails
            self.page = None
            self.browser = None
            self.playwright = None
