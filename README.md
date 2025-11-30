# Web Tools MCP Server

A Model Context Protocol (MCP) server that provides web browsing, searching, and content extraction capabilities using Playwright and SearXNG.

## Features

- **Web Search**: Search the web using a SearXNG instance
- **Page Navigation**: Navigate to URLs with optional element waiting
- **Content Extraction**: Extract clean text content from web pages
- **Text Summarization**: Summarize text using a local LLM (optional)
- **Combined Operations**: Fetch and extract page content in one operation

## Installation

1. Install Python dependencies:
```bash
pip install fastmcp playwright beautifulsoup4 llama-cpp-python
```

2. Install Playwright browsers:
```bash
playwright install
```

## Configuration

Create a `.env` file with the following optional variables:

```env
# SearXNG instance URL (default: http://192.168.77.8:8888)
SEARXNG_URL=http://your-searxng-instance:8888

# Path to local LLM model for summarization (optional)
LLM=/path/to/your/model.gguf
```

## Docker Deployment

The application can be deployed using Docker Compose, which uses `uv` for dependency management.

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (see Configuration section)

### Build and Run
```bash
docker-compose up --build
```

The server will be available at `http://localhost:9000`.

### Mounting Volumes
- The `.env` file is automatically loaded
- If using local LLM models, ensure the `models` directory is present in the project root and contains your model files (e.g., `Qwen3-4B-Q4_K_M.gguf`)

### Stopping the Container
```bash
docker-compose down
```

## Running the Server

### As MCP Server (stdio)
```bash
python main.py
```

### As HTTP Server
The server runs on `http://127.0.0.1:9000` by default.

## Available Tools

### 1. `web_search`
Perform web search using SearXNG.

**Parameters:**
- `query` (str): Search query string
- `max_results` (int, optional): Maximum number of results to return (default: 10)

**Returns:**
```json
{
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com",
      "snippet": "Page description..."
    }
  ]
}
```

### 2. `navigate`
Navigate to a URL and optionally wait for an element to appear.

**Parameters:**
- `url` (str): URL to navigate to
- `wait_for_element` (str, optional): CSS selector to wait for
- `wait_time` (int, optional): Maximum time to wait in seconds (default: 10)

**Returns:**
```json
{
  "status": "success",
  "message": "Navigated to https://example.com"
}
```

### 3. `extract_content`
Extract clean text content from a web page.

**Parameters:**
- `url` (str, optional): URL to extract content from (uses current page if not provided)
- `wait_for_element` (str, optional): CSS selector to wait for before extraction

**Returns:**
```json
{
  "content": "Extracted page text content..."
}
```

### 4. `get_page_content`
Navigate to a URL and extract its content in one operation.

**Parameters:**
- `url` (str): URL to fetch and extract content from

**Returns:**
```json
{
  "url": "https://example.com",
  "content": "Extracted page text content..."
}
```

### 5. `summarize`
Summarize text using a local LLM (requires LLM configuration).

**Parameters:**
- `text` (str): Text to summarize
- `max_tokens` (int, optional): Maximum tokens in summary (default: 200)

**Returns:**
```json
{
  "summary": "Concise summary of the text..."
}
```

### 6. `close_browser`
Close the browser instance and clean up resources.

**Returns:**
```json
{
  "status": "success",
  "message": "Browser closed successfully"
}
```

## Architecture

The server uses a singleton pattern to maintain a single browser instance across multiple tool calls, which improves performance and resource usage. The browser is automatically initialized on first use and can be explicitly closed using the `close_browser` tool.

### Key Components

- **main.py**: MCP server implementation with tool definitions
- **browser_tool.py**: Browser automation and web interaction logic
- **tests/**: Unit tests for both server and browser tools

## Development

### Running Tests
```bash
pytest tests/
```

### Testing Individual Tools
Use the MCP inspector or connect to the server using an MCP client to test individual tools.

## Troubleshooting

### Browser fails to launch
- Ensure Playwright is installed: `playwright install`
- Check that Chromium is installed: `playwright install chromium`

### SearXNG search fails
- Verify your SearXNG instance is running and accessible
- Check the SEARXNG_URL environment variable
- Ensure the instance is configured to return JSON results

### Summarization fails
- Make sure the LLM environment variable points to a valid model file
- Ensure llama-cpp-python is installed correctly for your system
- Check model file permissions and path

## License

MIT