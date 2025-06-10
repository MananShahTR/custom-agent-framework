# Enhanced Web Search Agent with Brave Search & Firecrawl

A powerful web search and content extraction agent built with Claude Sonnet 4, featuring integration with Brave Search API for high-quality search results and Firecrawl for advanced content extraction.

## 🚀 Key Features

### Advanced Search Capabilities
- **Brave Search Integration**: High-quality, recent search results with comprehensive coverage
- **Intelligent Fallback**: Automatic fallback to DuckDuckGo when Brave API is unavailable
- **Configurable Parameters**: Control search count, geographic region, and result freshness
- **Mixed Results**: Combines web results with relevant news articles

### Enhanced Content Extraction
- **Firecrawl Integration**: Professional-grade content extraction with clean markdown output
- **Smart HTML Parsing**: Advanced content detection and unwanted element removal
- **Customizable Extraction**: Configure included/excluded HTML tags and output formats
- **Intelligent Fallback**: BeautifulSoup-based extraction when Firecrawl is unavailable

### Advanced Agent Features
- **Context Management**: Intelligent conversation history with token tracking
- **Parallel Tool Execution**: Efficient concurrent processing of multiple operations
- **Comprehensive Logging**: Detailed verbose mode for debugging and monitoring
- **API Key Management**: Graceful handling of missing API keys with fallback options

## 📦 Installation

### Prerequisites
```bash
Python 3.9+
pip package manager
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Dependencies
```
anthropic>=0.21.0
requests>=2.28.0
python-dotenv>=0.19.0
firecrawl-py>=0.0.8
beautifulsoup4>=4.12.0
```

## 🔑 API Key Configuration

Create a `.env` file in your project directory:

```env
# Required for basic functionality
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional - for enhanced search (fallback available)
BRAVE_SEARCH_API_KEY=your_brave_search_api_key_here

# Optional - for enhanced content extraction (fallback available)
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### Where to Get API Keys

1. **Anthropic API** (Required): [console.anthropic.com](https://console.anthropic.com/)
2. **Brave Search API** (Recommended): [api.search.brave.com](https://api.search.brave.com/)
3. **Firecrawl API** (Recommended): [firecrawl.dev](https://www.firecrawl.dev/)

## 🎯 Usage Examples

### Basic Usage

```python
from web_search_agent import WebSearchAgent

# Initialize the agent
agent = WebSearchAgent(verbose=True)

# Perform research query
response = agent.run("What are the latest developments in quantum computing?")

# Extract text response
text_content = ""
for block in response.content:
    if block.type == "text":
        text_content += block.text

print(text_content)
```

### Direct Tool Usage

```python
# Direct web search
search_results = agent.search_web("machine learning trends 2024", count=5)
print(search_results)

# Direct content extraction
content = agent.extract_content("https://example.com/article", max_length=3000)
print(content)
```

### Advanced Configuration

```python
from web_search_agent import WebSearchAgent, ModelConfig

# Custom configuration
config = ModelConfig(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    temperature=0.1,  # More focused responses
    context_window_tokens=180000
)

# Specialized research agent
agent = WebSearchAgent(
    name="ResearchAssistant",
    config=config,
    verbose=True
)
```

### Custom System Prompt

```python
research_prompt = """You are a specialized research assistant with advanced web search capabilities.

**Research Strategy:**
1. Use multiple targeted searches for comprehensive coverage
2. Extract detailed content from authoritative sources
3. Cross-reference information from multiple sources
4. Provide well-structured responses with proper citations
5. Assess source credibility and recency

**Response Format:**
- Executive summary of key findings
- Detailed analysis with source citations
- Assessment of source quality
- Implications and future research directions
"""

agent = WebSearchAgent(
    name="AdvancedResearcher",
    system=research_prompt,
    verbose=True
)
```

## 🛠 Tool Specifications

### BraveSearchTool

**Purpose**: High-quality web search with recent, relevant results

**Parameters**:
- `query` (required): Search query string
- `count` (optional): Number of results (1-20, default: 5)
- `offset` (optional): Result offset for pagination (default: 0)
- `country` (optional): Country code for localized results (default: "US")

**Features**:
- Recent web results with publication dates
- News integration for current events
- Geographic result customization
- Automatic fallback to DuckDuckGo

### FirecrawlContentTool

**Purpose**: Advanced content extraction from web pages

**Parameters**:
- `url` (required): Target URL for content extraction
- `formats` (optional): Output formats ["markdown", "html", "rawHtml"]
- `include_tags` (optional): HTML tags to include in extraction
- `exclude_tags` (optional): HTML tags to exclude from extraction
- `max_length` (optional): Maximum content length (500-50000, default: 8000)

**Features**:
- Clean markdown output
- Intelligent content detection
- Metadata extraction (title, description)
- Automatic fallback to BeautifulSoup

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_enhanced_web_search_agent.py
```

### Test Coverage
- API key configuration validation
- Individual tool functionality
- Agent initialization and setup
- Real API integration (when keys available)
- Parameter validation
- Error handling and fallbacks

## 📚 Examples and Demos

### Interactive Demo
```bash
python web_search_example.py
```

### Research Examples
```python
# Current events research
response = agent.run("Find the latest research on climate change impacts published in 2024")

# Technical analysis
response = agent.run("Research the current state of autonomous vehicle safety systems, extract content from recent studies")

# Multi-source verification
response = agent.run("Compare different perspectives on AI regulation from government and industry sources")
```

## 🏗 Architecture

### Core Components

1. **ModelConfig**: Claude model configuration and parameters
2. **Tool Base Class**: Abstract interface for all agent tools
3. **BraveSearchTool**: Advanced web search implementation
4. **FirecrawlContentTool**: Professional content extraction
5. **MessageHistory**: Conversation management with token tracking
6. **WebSearchAgent**: Main agent orchestrating tools and responses

### Message Flow

```
User Query → Agent → Tool Selection → Parallel Execution → Response Synthesis
           ↓
    Tool Results → Content Processing → Context Update → Final Response
```

### Error Handling

- **API Failures**: Automatic fallback to alternative services
- **Rate Limiting**: Intelligent retry mechanisms
- **Content Errors**: Graceful degradation with partial results
- **Network Issues**: Timeout handling and error reporting

## 🔧 Advanced Features

### Parallel Tool Execution
```python
# Tools are executed concurrently for optimal performance
# Multiple searches and extractions happen simultaneously
```

### Context Management
```python
# Automatic context window management
# Token tracking and history truncation
# Conversation continuity across long sessions
```

### Intelligent Fallbacks
```python
# Brave Search → DuckDuckGo fallback
# Firecrawl → BeautifulSoup fallback
# Graceful degradation without failures
```

## 🚨 Rate Limiting and Best Practices

### API Usage Guidelines

1. **Brave Search**: 1000 requests/month on free tier
2. **Firecrawl**: Varies by plan (check your dashboard)
3. **Anthropic**: Rate limits apply based on your plan

### Optimization Tips

- Use appropriate `count` parameters to minimize API calls
- Leverage direct tool methods for simple operations
- Configure `max_length` based on your needs
- Use verbose mode for debugging, disable for production

### Error Handling Best Practices

```python
try:
    response = agent.run(query)
    # Process response
except Exception as e:
    print(f"Agent error: {e}")
    # Handle gracefully
```

## 🔒 Security Considerations

- Store API keys in `.env` files, never in code
- Use environment variable validation
- Implement request timeouts
- Validate URLs before content extraction
- Monitor API usage and costs

## 🐛 Troubleshooting

### Common Issues

**"BRAVE_SEARCH_API_KEY not found"**
- Add your Brave Search API key to `.env`
- The agent will use DuckDuckGo fallback automatically

**"FIRECRAWL_API_KEY not found"**
- Add your Firecrawl API key to `.env`
- The agent will use BeautifulSoup fallback automatically

**"503 Server Error"**
- Target website is temporarily unavailable
- Try a different URL or retry later

**Token limit exceeded**
- Reduce `max_tokens` in ModelConfig
- Use shorter `max_length` for content extraction

### Performance Optimization

- Enable API keys for optimal results
- Use appropriate timeout values
- Monitor token usage in verbose mode
- Adjust temperature for response style

## 📈 Monitoring and Analytics

### Built-in Metrics
- Token usage tracking
- API response times
- Success/failure rates
- Fallback usage statistics

### Logging
```python
# Enable detailed logging
agent = WebSearchAgent(verbose=True)

# Monitor tool execution
# Track API usage
# Debug response quality
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Related Projects

- [Anthropic Quickstarts](https://github.com/anthropics/anthropic-quickstarts)
- [Brave Search API](https://api.search.brave.com/)
- [Firecrawl](https://www.firecrawl.dev/)

---

**Built with ❤️ using Claude Sonnet 4, Brave Search, and Firecrawl** 