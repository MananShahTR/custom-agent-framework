# Web Search Agent

A powerful Claude-powered agent with web search capabilities, built following the [Anthropic quickstarts agent pattern](https://github.com/anthropics/anthropic-quickstarts/blob/main/agents/agent.py).

## Features

🔍 **Web Search**: Search the web for current information using DuckDuckGo's Instant Answer API  
🌐 **URL Content Fetching**: Extract text content from any URL  
🧠 **Intelligent Responses**: Claude processes search results to provide comprehensive answers  
⚡ **Async Support**: Built with asyncio for efficient parallel tool execution  
📊 **Token Management**: Automatic context window management with message history truncation  
🎛️ **Configurable**: Customizable system prompts, model parameters, and tool sets  

## Architecture

This implementation follows the Anthropic quickstarts pattern with:

- **Tool-based Architecture**: Modular tools that can be easily extended
- **Message History Management**: Automatic token tracking and context management
- **Parallel Tool Execution**: Execute multiple tools simultaneously for efficiency
- **Error Handling**: Robust error handling with fallback mechanisms

## Installation

1. **Clone or download the files**:
   - `web_search_agent.py` - Main agent implementation
   - `web_search_example.py` - Usage examples
   - `requirements.txt` - Dependencies

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Anthropic API key**:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Quick Start

### Basic Usage

```python
from web_search_agent import WebSearchAgent

# Initialize the agent
agent = WebSearchAgent(verbose=True)

# Ask a question that requires web search
response = agent.run("What are the latest developments in artificial intelligence?")

# Extract the text response
text_content = ""
for block in response.content:
    if block.type == "text":
        text_content += block.text

print(text_content)
```

### Direct Tool Usage

```python
# Direct web search
search_result = agent.search_web("Python 3.12 new features", max_results=3)
print(search_result)

# Fetch content from a specific URL
content = agent.fetch_url("https://example.com/article")
print(content)
```

### Custom Configuration

```python
from web_search_agent import WebSearchAgent, ModelConfig

# Custom agent with specific configuration
agent = WebSearchAgent(
    name="ResearchAssistant",
    config=ModelConfig(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        temperature=0.2  # More focused responses
    ),
    verbose=True
)
```

## Available Tools

### 1. WebSearchTool
- **Name**: `web_search`
- **Description**: Search the web for current information
- **Parameters**:
  - `query` (required): The search query
  - `max_results` (optional): Maximum number of results (default: 5)

### 2. URLContentTool
- **Name**: `fetch_url_content`
- **Description**: Fetch and extract text content from URLs
- **Parameters**:
  - `url` (required): The URL to fetch
  - `max_length` (optional): Maximum content length (default: 2000)

## Advanced Usage

### Custom System Prompt

```python
research_prompt = """You are a specialized research assistant focused on scientific topics.

When conducting research:
1. Always search for the most recent and authoritative sources
2. Provide detailed explanations with proper citations
3. Compare multiple sources when possible
4. Highlight any limitations or uncertainties in the information

Your responses should be thorough, well-structured, and academically rigorous."""

agent = WebSearchAgent(
    name="ScienceResearcher",
    system=research_prompt,
    verbose=True
)
```

### Adding Custom Tools

```python
from web_search_agent import Tool, WebSearchAgent

class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Description of what this tool does",
            input_schema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    
    async def execute(self, param: str) -> str:
        # Your custom tool logic here
        return f"Result for: {param}"

# Add to agent
custom_tools = [WebSearchTool(), URLContentTool(), CustomTool()]
agent = WebSearchAgent(tools=custom_tools)
```

## Example Queries

The agent can handle various types of research questions:

- **Current Events**: "What are the latest developments in quantum computing?"
- **Technical Information**: "Explain the new features in Python 3.12"
- **Market Research**: "What are the current trends in renewable energy?"
- **Academic Research**: "What recent studies have been published about machine learning in healthcare?"
- **Fact Checking**: "What is the current status of SpaceX's Mars mission plans?"

## Architecture Details

### Based on Anthropic Quickstarts

This implementation is based on the [official Anthropic quickstarts agent pattern](https://github.com/anthropics/anthropic-quickstarts/blob/main/agents/agent.py) with the following components:

1. **Tool Base Class**: Standardized tool interface
2. **Message History**: Token-aware conversation management
3. **Agent Loop**: Handles tool execution and response generation
4. **Configuration**: Flexible model and behavior configuration

### Key Components

```
web_search_agent.py
├── ModelConfig          # Model configuration dataclass
├── Tool                 # Base tool class
├── WebSearchTool        # Web search implementation
├── URLContentTool       # URL content fetching
├── MessageHistory       # Conversation management
├── execute_tools        # Parallel tool execution
└── WebSearchAgent       # Main agent class
```

## Configuration Options

### ModelConfig

```python
@dataclass
class ModelConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 1.0
    context_window_tokens: int = 180000
```

### Agent Parameters

- `name`: Agent identifier for logging
- `system`: Custom system prompt
- `tools`: List of available tools
- `config`: Model configuration
- `verbose`: Enable detailed logging
- `client`: Custom Anthropic client
- `message_params`: Additional API parameters

## Error Handling

The agent includes robust error handling:

- **Network Errors**: Graceful handling of connection timeouts
- **API Errors**: Proper error messages for API failures
- **Tool Errors**: Individual tool failures don't crash the agent
- **Rate Limiting**: Built-in retry logic for API rate limits

## Limitations

1. **Search API**: Uses DuckDuckGo Instant Answer API which may have limited results for some queries
2. **Content Extraction**: Basic HTML parsing - complex JavaScript sites may not work well
3. **Rate Limits**: Subject to both Anthropic API and search API rate limits
4. **Real-time Data**: Search results may not be completely real-time

## Contributing

To extend the agent with new tools:

1. Create a new tool class inheriting from `Tool`
2. Implement the `execute` method
3. Add appropriate input schema
4. Add to the agent's tool list

## License

This code is provided as an example and follows the same license terms as the Anthropic quickstarts repository.

## References

- [Anthropic Quickstarts Repository](https://github.com/anthropics/anthropic-quickstarts)
- [Claude API Documentation](https://docs.anthropic.com/)
- [DuckDuckGo Instant Answer API](https://duckduckgo.com/api)

---

**Note**: This agent requires an Anthropic API key and internet access for web search functionality. 