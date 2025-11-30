import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch, AsyncMock as AsyncMockType
from browser_tool import BrowserTool


@pytest.fixture
def browser_tool():
    return BrowserTool()


@pytest.mark.asyncio
async def test_setup_browser(browser_tool):
    """Test that _setup_browser initializes playwright, browser, and page"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        await browser_tool._setup_browser()

        assert browser_tool.playwright == mock_pw_instance
        assert browser_tool.browser == mock_browser
        assert browser_tool.page == mock_page


@pytest.mark.asyncio
async def test_web_search_success(browser_tool):
    """Test successful web search with mock response"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response

        # Mock page content with JSON
        mock_page.content.return_value = '''
        <html><body><pre>{"results": [{"title": "Test Title", "url": "http://test.com", "content": "Test content"}]}</pre></body></html>
        '''

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        results = await browser_tool.web_search("test query")

        assert len(results) == 1
        assert results[0]['title'] == "Test Title"
        assert results[0]['url'] == "http://test.com"
        assert results[0]['snippet'] == "Test content"


@pytest.mark.asyncio
async def test_web_search_no_results(browser_tool):
    """Test web search when no results are found"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response

        # Mock page content with empty results
        mock_page.content.return_value = '''
        <html><body><pre>{"results": []}</pre></body></html>
        '''

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        results = await browser_tool.web_search("test query")

        assert results == []


@pytest.mark.asyncio
async def test_web_search_failure(browser_tool):
    """Test web search when request fails"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_response = MagicMock()
        mock_response.status = 404
        mock_page.goto.return_value = mock_response

        results = await browser_tool.web_search("test query")

        assert results == []


@pytest.mark.asyncio
async def test_navigate_success(browser_tool):
    """Test successful navigation"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        await browser_tool.navigate("http://test.com")

        mock_page.goto.assert_called_once_with("http://test.com", wait_until="domcontentloaded", timeout=30000)


@pytest.mark.asyncio
async def test_navigate_with_wait_element(browser_tool):
    """Test navigation with element waiting"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        await browser_tool.navigate("http://test.com", wait_for_element="#test")

        mock_page.goto.assert_called_once_with("http://test.com", wait_until="domcontentloaded", timeout=30000)
        mock_page.wait_for_selector.assert_called_once_with("#test", timeout=10000)


@pytest.mark.asyncio
async def test_navigate_element_not_found(browser_tool):
    """Test navigation when element is not found"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_page.wait_for_selector.side_effect = Exception("Timeout")

        with pytest.raises(Exception, match="Element '#test' not found on page"):
            await browser_tool.navigate("http://test.com", wait_for_element="#test")


@pytest.mark.asyncio
async def test_extract_content_with_url(browser_tool):
    """Test content extraction with URL navigation"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        mock_page.content.return_value = '''
        <html><body><h1>Test Title</h1><p>Test content</p><script>console.log('test');</script></body></html>
        '''

        content = await browser_tool.extract_content("http://test.com")

        assert "Test Title" in content
        assert "Test content" in content
        assert "console.log" not in content  # Script should be removed


@pytest.mark.asyncio
async def test_extract_content_without_url(browser_tool):
    """Test content extraction without URL (current page)"""
    with patch('browser_tool.async_playwright') as mock_async_playwright:
        mock_pw_instance = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        # Mock the async_playwright function itself
        mock_async_playwright.return_value = AsyncMock()
        mock_async_playwright.return_value.start.return_value = mock_pw_instance

        mock_page.content.return_value = '''
        <html><body><h1>Test Title</h1><p>Test content</p></body></html>
        '''

        content = await browser_tool.extract_content()

        assert "Test Title" in content
        assert "Test content" in content


@pytest.mark.asyncio
async def test_summarize_with_llm(browser_tool):
    """Test text summarization with LLM"""
    mock_llm = MagicMock()
    mock_llm.return_value = {"choices": [{"text": "Summary text"}]}
    browser_tool.llm = mock_llm

    result = await browser_tool.summarize("Long text to summarize")

    assert result == "Summary text"
    mock_llm.assert_called_once()


@pytest.mark.asyncio
async def test_summarize_no_llm(browser_tool):
    """Test summarization when LLM is not configured"""
    browser_tool.llm = None

    with pytest.raises(Exception, match="LLM not configured"):
        await browser_tool.summarize("Text")


@pytest.mark.asyncio
async def test_close(browser_tool):
    """Test closing browser and playwright"""
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    browser_tool.browser = mock_browser
    browser_tool.playwright = mock_playwright

    await browser_tool.close()

    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()


@pytest.mark.asyncio
async def test_close_no_browser(browser_tool):
    """Test closing when browser is not initialized"""
    browser_tool.browser = None
    browser_tool.playwright = None

    await browser_tool.close()

    # Should not raise any exceptions


@pytest.mark.asyncio
async def test_model_loaded_when_configured():
    """Test that LLM model is loaded when LLM environment variable is set"""
    with patch.dict(os.environ, {'LLM': '/path/to/model.gguf'}):
        with patch('os.path.exists', return_value=True):
            with patch('browser_tool.Llama') as mock_llama:
                mock_llama_instance = MagicMock()
                mock_llama.return_value = mock_llama_instance
                
                browser_tool = BrowserTool()
                
                assert browser_tool.llm is not None
                assert browser_tool.llm == mock_llama_instance
                mock_llama.assert_called_once_with(model_path='/path/to/model.gguf', n_ctx=2048, n_threads=4)


@pytest.mark.asyncio
async def test_model_not_loaded_when_not_configured():
    """Test that LLM model is not loaded when LLM environment variable is not set"""
    with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
        browser_tool = BrowserTool()
        
        assert browser_tool.llm is None


@pytest.mark.asyncio
async def test_model_not_loaded_when_file_not_exists():
    """Test that LLM model is not loaded when model file doesn't exist"""
    with patch.dict(os.environ, {'LLM': '/path/to/nonexistent/model.gguf'}):
        with patch('os.path.exists', return_value=False):
            browser_tool = BrowserTool()
            
            assert browser_tool.llm is None


@pytest.mark.asyncio
async def test_model_loading_error_handling():
    """Test that model loading errors are handled gracefully"""
    with patch.dict(os.environ, {'LLM': '/path/to/model.gguf'}):
        with patch('os.path.exists', return_value=True):
            with patch('browser_tool.Llama') as mock_llama:
                mock_llama.side_effect = Exception("Model loading failed")
                
                browser_tool = BrowserTool()
                
                assert browser_tool.llm is None