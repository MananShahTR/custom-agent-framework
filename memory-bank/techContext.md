# Technical Context: Custom AI Agents Framework

## Technology Stack

### Core Dependencies
```python
# Core AI and HTTP libraries
anthropic>=0.35.0        # Claude API client
python-dotenv>=1.0.0     # Environment variable management
requests>=2.31.0         # HTTP requests

# MCP (Model Context Protocol) server integration
mcp>=1.0.0              # Model Context Protocol

# Web scraping and content extraction
beautifulsoup4>=4.12.0   # HTML parsing
firecrawl-py>=0.0.16     # Advanced web scraping

# Google Drive integration
google-auth>=2.23.0                    # Google authentication
google-auth-oauthlib>=1.1.0           # OAuth2 flow
google-auth-httplib2>=0.1.1           # HTTP transport
google-api-python-client>=2.100.0     # Google APIs

# Token counting and text processing
tiktoken>=0.5.0         # OpenAI tokenizer (used for Claude)

# Development and testing
pytest>=7.4.0           # Testing framework
pytest-asyncio>=0.21.0  # Async test support
```

### Python Requirements
- **Python 3.9+**: Required for modern async/await patterns and type hints
- **AsyncIO**: All I/O operations use async/await for performance
- **Type Hints**: Comprehensive typing for IDE support and maintainability

### External APIs

#### 1. **Anthropic Claude API**
- **Model**: `claude-3-5-sonnet-20241022` (default)
- **Authentication**: API key via `ANTHROPIC_API_KEY`
- **Features**: Function calling, large context windows (180K tokens)
- **Rate Limits**: Handled by client SDK

#### 2. **Brave Search API**
- **Purpose**: Web search for research agents
- **Authentication**: API key via `BRAVE_API_KEY`
- **Endpoints**: Web search with filtering and ranking
- **Rate Limits**: Varies by plan

#### 3. **Firecrawl API**
- **Purpose**: Advanced web content extraction
- **Authentication**: API key via `FIRECRAWL_API_KEY`
- **Features**: Clean content extraction, screenshot capture
- **Alternative**: BeautifulSoup fallback for basic extraction

#### 4. **Google Drive API**
- **Purpose**: Document access and content extraction
- **Authentication**: OAuth2 flow with `credentials.json`
- **Scopes**: Drive readonly access
- **Content Types**: Docs, Sheets, PDFs, Images

## Development Setup

### Environment Configuration
```bash
# Required environment variables
ANTHROPIC_API_KEY=your_anthropic_api_key
BRAVE_API_KEY=your_brave_search_api_key      # Optional
FIRECRAWL_API_KEY=your_firecrawl_api_key     # Optional

# Google Drive setup (optional)
# Run: python scripts/setup_google_drive.py
```

### Project Structure
```
custom-agent-framework/
├── .env                    # Environment variables
├── credentials.json        # Google OAuth credentials
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── src/                   # Core framework
│   ├── agents/           # Agent implementations
│   ├── tools/            # Tool implementations
│   └── utils/            # Utility modules
├── examples/             # Usage examples
├── tests/                # Test suite
├── scripts/              # Setup scripts
└── memory-bank/          # Project documentation
```

### Installation Process
```bash
# 1. Clone repository
git clone <repository-url>
cd custom-agent-framework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Optional: Setup Google Drive
python scripts/setup_google_drive.py

# 5. Run examples
python examples/basic_web_search.py
```

## Technical Constraints

### 1. **API Rate Limits**
- **Anthropic**: Varies by plan, handled by SDK
- **Brave Search**: 2000 requests/month (free tier)
- **Firecrawl**: 500 scrapes/month (free tier)
- **Google Drive**: 100 requests/100 seconds/user

### 2. **Memory Management**
- **Context Windows**: Claude supports 180K tokens
- **Token Counting**: Using tiktoken for estimation
- **Message History**: Managed per conversation
- **MCP Connections**: Proper cleanup required

### 3. **Network Dependencies**
- **Internet Required**: For all API calls
- **Timeouts**: 30s default for web requests
- **Retries**: Built-in retry logic for transient failures
- **Fallbacks**: BeautifulSoup for web scraping failures

### 4. **Security Considerations**
- **API Keys**: Environment variables only
- **OAuth Tokens**: Stored in credentials.json (local only)
- **Input Validation**: Tool parameter validation
- **Error Handling**: No sensitive data in error messages

## Tool Usage Patterns

### 1. **Web Search Pattern**
```python
# Auto-loaded with enable_web_search=True
agent = Agent(enable_web_search=True)

# Tools added automatically:
# - BraveSearchTool: Web search
# - FirecrawlContentTool: Content extraction
```

### 2. **Google Drive Pattern**
```python
# Auto-loaded with enable_google_drive=True
agent = Agent(enable_google_drive=True)

# Tools added automatically:
# - GoogleDriveTool: File search
# - GoogleDriveContentTool: Content extraction
```

### 3. **MCP Integration Pattern**
```python
# MCP servers configured at agent creation
mcp_servers = [{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
    "env": {}
}]

agent = Agent(mcp_servers=mcp_servers)
# MCP tools loaded lazily on first use
```

### 4. **Custom Tool Pattern**
```python
class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Does custom work"
        )
    
    async def execute(self, **kwargs) -> str:
        # Implementation
        return "Result"

agent = Agent(tools=[CustomTool()])
```

## Async Patterns

### 1. **Agent Execution**
```python
# All agent operations are async
response = await agent.run_async("Query")

# Sync wrapper available
response = agent.run("Query")  # Uses asyncio.run()
```

### 2. **Tool Execution**
```python
# Tools execute in parallel by default
tool_results = await agent.execute_tool_calls(tool_calls, parallel=True)

# Sequential execution when needed
tool_results = await agent.execute_tool_calls(tool_calls, parallel=False)
```

### 3. **Resource Cleanup**
```python
# Always cleanup MCP connections
try:
    response = await agent.run_async("Query")
finally:
    await agent.cleanup()

# Or use context manager pattern
async with agent:
    response = await agent.run_async("Query")
```

## Testing Infrastructure

### Test Categories
```python
# Unit tests
tests/test_basic.py         # Basic agent functionality
tests/test_approval.py      # Approval system tests

# Integration tests
tests/test_pdf_extraction.py  # Google Drive PDF handling

# Example tests
examples/                   # All examples are executable tests
```

### Testing Patterns
```python
# Async test support
@pytest.mark.asyncio
async def test_agent_creation():
    agent = Agent(name="Test", description="Test agent")
    assert agent.name == "Test"

# Mock external APIs for testing
@pytest.fixture
def mock_anthropic_client():
    return Mock(spec=Anthropic)
```

## Package Distribution

### Setup Configuration
```python
# setup.py
name="ai-agents-framework",
version="0.1.0",
python_requires=">=3.9",
install_requires=requirements,
entry_points={
    "console_scripts": [
        "ai-agents=src.cli:main",
    ],
}
```

### Development Dependencies
```python
extras_require={
    "dev": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "black",       # Code formatting
        "flake8",      # Linting
        "mypy",        # Type checking
    ],
}
```

This technical foundation provides a robust, scalable platform for AI agent development while maintaining simplicity and ease of use.
