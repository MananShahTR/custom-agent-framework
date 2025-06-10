# Project Brief: Custom AI Agents Framework

## Overview
A clean, modular Python framework for building AI agents powered by Claude (Anthropic), featuring extensible tool integration, MCP (Model Context Protocol) support, and specialized agent types for various use cases.

## Core Purpose
- **Simplify AI Agent Development**: Provide clean abstractions for building custom AI agents
- **Enable Tool Integration**: Support multiple tool types including web search, Google Drive, and MCP servers
- **Support Multiple Agent Types**: From basic conversational agents to specialized research agents
- **Facilitate Multi-Agent Systems**: Enable agent handoffs and coordination

## Key Features
1. **Modular Agent Architecture**: Clean base classes with specialized implementations
2. **MCP Integration**: Connect to external tools and services via Model Context Protocol
3. **Web Search Capabilities**: Built-in web search with Brave Search and Firecrawl
4. **Google Drive Integration**: Native document access and content extraction
5. **Deep Research Agents**: Specialized agents for comprehensive research with citations
6. **Multi-Agent Systems**: Agent coordination and handoff capabilities
7. **Human-in-the-Loop**: Approval mechanisms for sensitive operations
8. **Persistent Message History**: Conversation management across sessions

## Target Use Cases
- **Research Assistants**: Deep research with web search and document analysis
- **Content Creators**: Web scraping and content extraction
- **Document Processors**: Google Drive integration for document workflows
- **Custom Workflows**: Extensible framework for domain-specific agents
- **Multi-Agent Applications**: Coordinated agent systems

## Technical Stack
- **Core**: Python 3.9+, Anthropic Claude API
- **MCP**: Model Context Protocol for external tool integration
- **Web**: Brave Search API, Firecrawl for content extraction
- **Google**: Google Drive API, OAuth2 authentication
- **Testing**: pytest, pytest-asyncio

## Project Structure
```
├── src/                    # Core framework code
│   ├── agents/            # Agent implementations
│   ├── tools/             # Tool implementations  
│   └── utils/             # Utility modules
├── examples/              # Usage examples and demos
├── tests/                 # Test suite
├── scripts/               # Setup and utility scripts
└── memory-bank/           # Project documentation and context
```

## Success Criteria
- ✅ Clean, intuitive API for agent creation
- ✅ Extensible tool system
- ✅ Robust MCP integration
- ✅ Comprehensive examples and documentation
- ✅ Production-ready error handling and logging
