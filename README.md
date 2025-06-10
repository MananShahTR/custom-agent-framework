# AI Agents Framework

A clean, modular framework for building AI agents with Claude, featuring MCP (Model Context Protocol) integration, web search capabilities, and Google Drive integration.

## Features

- 🤖 **Modular Agent Architecture**: Clean, extensible base classes for building custom agents
- 🔌 **MCP Integration**: Connect to external tools and services via Model Context Protocol
- 🌐 **Web Search**: Built-in web search capabilities with Brave Search and Firecrawl
- 📁 **Google Drive**: Native Google Drive integration for document access
- 🧠 **Deep Research**: Specialized agents for comprehensive research tasks
- 🔄 **Message History**: Persistent conversation management
- 🛠️ **Custom Tools**: Easy-to-extend tool system

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd anthropic-tests

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.agents import Agent

# Create a simple agent
agent = Agent(
    name="My Assistant",
    description="A helpful AI assistant",
    verbose=True
)

# Use the agent
response = await agent.run_async("Hello! How can you help me today?")
print(response)
```

### With Web Search

```python
from src.agents import Agent

agent = Agent(
    name="Research Assistant",
    description="An agent that can search the web for information",
    enable_web_search=True,
    verbose=True
)

response = await agent.run_async("What are the latest developments in AI?")
```

### With MCP Integration

```python
from src.agents import Agent

# Configure MCP servers
mcp_servers = [
    {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
        "env": {}
    }
]

agent = Agent(
    name="File Assistant",
    description="An agent with file system access",
    mcp_servers=mcp_servers,
    verbose=True
)

response = await agent.run_async("List the files in my project directory")
```

## Project Structure

```
├── src/                    # Main source code
│   ├── agents/            # Agent implementations
│   ├── tools/             # Tool implementations
│   └── utils/             # Utility modules
├── examples/              # Example scripts and demos
├── tests/                 # Test files
├── scripts/               # Setup and utility scripts
├── archive/               # Archived/legacy code
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Available Agents

### Base Agent
The foundation for all other agents with core functionality.

### Web Search Agent
Specialized for web search and content extraction tasks.

### Deep Research Agent
Advanced agent for comprehensive research with configurable depth and focus.

## Available Tools

### Web Search Tools
- **BraveSearchTool**: Web search using Brave Search API
- **FirecrawlContentTool**: Content extraction from web pages

### Google Drive Tools
- **GoogleDriveTool**: Access and search Google Drive files
- **GoogleDriveContentTool**: Extract content from Google Drive documents

### MCP Tools
Dynamic tools loaded from MCP servers for extended functionality.

## Examples

Check the `examples/` directory for comprehensive examples:

- `basic_web_search.py` - Simple web search example
- `deep_research.py` - Advanced research agent
- `mcp_example.py` - MCP integration example
- `human_in_the_loop.py` - Interactive agent example
- `simple_multi_agent.py` - Multi-agent coordination

## Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
BRAVE_API_KEY=your_brave_search_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Google Drive Setup

For Google Drive integration, run the setup script:

```bash
python scripts/setup_google_drive.py
```

## MCP Integration

This framework supports MCP (Model Context Protocol) for connecting external tools and services. See [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for detailed documentation.

## Citation Features

The framework includes advanced citation capabilities. See [CITATION_FEATURES.md](CITATION_FEATURES.md) for details on how to use citation features in your agents.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_basic.py
```

### Adding Custom Tools

1. Create a new tool class inheriting from `Tool`
2. Implement the required methods
3. Add your tool to an agent's tool list

Example:
```python
from src.tools.base import Tool

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Description of what this tool does"
        )
    
    async def execute(self, **kwargs):
        # Your tool logic here
        return "Tool result"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

[Add support information here] 