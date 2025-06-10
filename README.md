# Storm Agent 🌩️

**Unleash the Power of AI Agents**

A powerful, production-ready framework for building intelligent AI agents with Claude. Storm Agent provides everything you need to create sophisticated agents that can search the web, process documents, integrate with external services, and coordinate with other agents.

[![PyPI version](https://badge.fury.io/py/storm-agent.svg)](https://badge.fury.io/py/storm-agent)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚡ Key Features

- 🚀 **Production Ready**: Battle-tested framework with comprehensive error handling
- 🤖 **Multiple Agent Types**: Basic, Web Search, Deep Research, and Multi-Agent systems
- 🌐 **Web Intelligence**: Advanced web search with Brave Search and Firecrawl content extraction
- 📁 **Document Processing**: Native Google Drive integration with OAuth2 authentication
- 🔌 **MCP Protocol**: Connect to external tools and services via Model Context Protocol
- 🧠 **Deep Research**: AI-powered research with citations and structured reports
- 🔄 **Multi-Agent Coordination**: Agent handoffs and collaborative workflows
- 🛡️ **Human-in-the-Loop**: Built-in approval mechanisms for sensitive operations
- 📈 **Async Performance**: Parallel tool execution and non-blocking operations

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install storm-agent

# Or install with development dependencies
pip install storm-agent[dev]
```

### Basic Usage

```python
from storm_agent import Agent

# Create a powerful AI agent
storm = Agent(
    name="My Storm Agent",
    description="A helpful AI assistant",
    verbose=True
)

# Unleash the storm
response = await storm.run_async("Hello! How can you help me today?")
print(response)

# Or use the synchronous version
response = storm.run("What's the weather like?")
```

### Web Search Agent

```python
from storm_agent import Agent, WebSearchAgent

# Quick web search setup
storm = Agent(
    name="Research Storm",
    description="Web research specialist",
    enable_web_search=True,
    verbose=True
)

# Or use the specialized WebSearchAgent
researcher = WebSearchAgent(
    name="Web Researcher",
    description="Specialized web search agent"
)

response = await researcher.run_async("What are the latest developments in AI?")
```

### Advanced Research Agent

```python
from storm_agent import DeepResearchAgent

# Create a research powerhouse
research_storm = DeepResearchAgent(
    name="Research Storm",
    description="Deep research specialist with citations",
    enable_web_search=True,
    enable_google_drive=True,
    verbose=True
)

# Get comprehensive research with citations
response = await research_storm.run_async(
    "Analyze the impact of renewable energy on global markets"
)
```

### MCP Integration

```python
from storm_agent import Agent

# Configure MCP servers for external tool access
mcp_servers = [
    {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
        "env": {}
    }
]

storm = Agent(
    name="File Storm",
    description="Agent with file system access",
    mcp_servers=mcp_servers,
    verbose=True
)

response = await storm.run_async("List and analyze the files in my project directory")
```

## 🏗️ Architecture

Storm Agent is built with a clean, modular architecture:

```
storm-agent/
├── src/storm_agent/       # Core framework
│   ├── agents/           # Agent implementations
│   ├── tools/            # Tool implementations
│   ├── utils/            # Utility modules
│   └── cli.py            # Command-line interface
├── examples/             # Usage examples and demos
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation
└── scripts/              # Setup and utility scripts
```

## 🤖 Available Agents

### Agent (General Purpose)
The versatile foundation agent that can be configured with any combination of tools.

### WebSearchAgent
Optimized for web research tasks with built-in search and content extraction capabilities.

### DeepResearchAgent
Advanced research specialist that provides comprehensive analysis with citations and structured reports.

### MultiAgentSystem
Orchestrates multiple agents for complex, multi-step workflows with intelligent task delegation.

## 🛠️ Built-in Tools

### Web Intelligence
- **BraveSearchTool**: High-quality web search with ranking and filtering
- **FirecrawlContentTool**: Advanced content extraction with fallback mechanisms

### Document Processing
- **GoogleDriveTool**: Search and access Google Drive files with OAuth2
- **GoogleDriveContentTool**: Extract content from Docs, Sheets, PDFs, and images

### System Integration
- **RequestApprovalTool**: Human-in-the-loop approval for sensitive operations
- **HandoffTool**: Seamless agent-to-agent task delegation
- **MCPTool**: Dynamic integration with Model Context Protocol servers

## 📚 Examples

Explore the `examples/` directory for comprehensive demonstrations:

- **`basic_web_search.py`** - Simple web search and content extraction
- **`deep_research.py`** - Advanced research with citations
- **`mcp_example.py`** - External tool integration via MCP
- **`human_in_the_loop.py`** - Interactive approval workflows
- **`simple_multi_agent.py`** - Multi-agent coordination patterns
- **`custom_agent.py`** - Building custom agent types
- **`handoff_basics.py`** - Agent handoff mechanisms

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional - for web search capabilities
BRAVE_API_KEY=your_brave_search_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Google Drive Integration

For Google Drive access, set up OAuth2 credentials:

```bash
# Run the setup script
python -m storm_agent.scripts.setup_google_drive

# Or if installed from source
python scripts/setup_google_drive.py
```

## 🔌 MCP Integration

Storm Agent has first-class support for the Model Context Protocol (MCP), enabling seamless integration with external tools and services. Connect to file systems, databases, APIs, and more.

See our [MCP Integration Guide](MCP_INTEGRATION.md) for detailed documentation.

## 📖 Citation System

Storm Agent includes a sophisticated citation system for research tasks, providing:
- Automatic source tracking
- Reference formatting
- Citation verification
- Structured bibliography generation

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install storm-agent[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=storm_agent

# Run specific test categories
pytest -m "not integration"  # Skip integration tests
pytest -m "asyncio"          # Run only async tests
```

### Creating Custom Tools

Extend Storm Agent with your own tools:

```python
from storm_agent import Tool

class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="weather_lookup",
            description="Get current weather for a location"
        )
    
    async def execute(self, location: str, **kwargs) -> str:
        # Your weather API integration here
        return f"Weather in {location}: Sunny, 72°F"

# Use your custom tool
from storm_agent import Agent

storm = Agent(
    name="Weather Storm",
    tools=[WeatherTool()]
)
```

### Command Line Interface

```bash
# Check version
storm-agent --version

# Create and run an agent
storm-agent create --name "Research Assistant" --type research --web-search

# Run built-in examples
storm-agent run-example basic
storm-agent run-example research
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/storm-agent/storm-agent.git
cd storm-agent

# Install in development mode
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://storm-agent.readthedocs.io](https://storm-agent.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/storm-agent/storm-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/storm-agent/storm-agent/discussions)

## ⭐ Star History

If Storm Agent has been helpful for your projects, please consider giving it a star on GitHub!

---

**Storm Agent** - *Unleash the Power of AI Agents* 🌩️
