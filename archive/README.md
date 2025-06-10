# AI Agents Framework

A clean, modular framework for building AI agents with Claude, based on the [Anthropic quickstarts agents pattern](https://github.com/anthropics/anthropic-quickstarts/tree/main/agents).

## 🚀 Features

- **Modular Design**: Clean base classes for agents and tools
- **Pre-built Agents**: Web search and research agents
- **Multiple Sources**: Web search, content extraction, Google Drive
- **Easy Extension**: Create custom agents and tools
- **Message History**: Automatic conversation management
- **Async Support**: Full async/await with sync wrappers

## 📦 Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up `.env` with your `ANTHROPIC_API_KEY`
3. Run examples:

```python
from src.agents import WebSearchAgent

agent = WebSearchAgent(verbose=True)
response = agent.run("What are the latest AI developments?")
```

## 🏗️ Architecture

- **`Agent`**: Base class for all agents
- **`Tool`**: Base class for all tools  
- **`WebSearchAgent`**: Web search specialist
- **`DeepResearchAgent`**: Multi-source research
- **Tools**: Brave Search, Firecrawl, Google Drive

## 📁 Structure

```
src/
├── agents/         # Agent implementations
├── tools/          # Tool implementations  
├── utils/          # Utilities
└── __init__.py
examples/           # Usage examples
```

## 🔧 Environment Variables

```bash
ANTHROPIC_API_KEY=your_key_here
BRAVE_SEARCH_API_KEY=optional
FIRECRAWL_API_KEY=optional
GOOGLE_SERVICE_ACCOUNT_FILE=optional
```

## 📚 Examples

- `examples/basic_web_search.py`: Basic web search
- `examples/deep_research.py`: Multi-source research
- `examples/custom_agent.py`: Build custom agents

Based on Anthropic's quickstarts pattern with clean, extensible design.

## 🔒 Authentication

### Google Drive Setup

1. Create a Google Cloud project
2. Enable the Google Drive API
3. Create service account credentials
4. Download the JSON key file
5. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to the path of your JSON file

Or use OAuth2:
1. Run the Google Drive setup script: `python setup_google_drive_auth.py`
2. Follow the authentication flow

### API Keys

Set the following in your `.env` file:

```bash
ANTHROPIC_API_KEY=your_anthropic_key
BRAVE_SEARCH_API_KEY=your_brave_search_key  # Optional
FIRECRAWL_API_KEY=your_firecrawl_key        # Optional
```

## 🧪 Testing

Run tests with:

```bash
python -m pytest tests/
```

## 📈 Features

- ✅ Base Agent and Tool classes
- ✅ Web search and content extraction
- ✅ Google Drive integration
- ✅ Message history management
- ✅ Token tracking and context management
- ✅ Async/sync support
- ✅ Comprehensive examples
- ✅ Error handling and fallbacks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by [Anthropic's quickstarts agents pattern](https://github.com/anthropics/anthropic-quickstarts/tree/main/agents)
- Built with [Anthropic's Claude API](https://www.anthropic.com/)
- Uses [Brave Search API](https://search.brave.com/search-api) for web search
- Uses [Firecrawl](https://firecrawl.dev/) for content extraction 