# Memory Bank: Custom AI Agents Framework

## Overview
This memory bank contains comprehensive documentation for a **production-ready Custom AI Agents Framework** built with Python and Claude (Anthropic). The framework provides clean, modular abstractions for building AI agents with extensive tool integration capabilities.

## Memory Bank Structure

### Core Files (Required Reading)
1. **[projectbrief.md](projectbrief.md)** - Foundation document defining project scope and goals
2. **[productContext.md](productContext.md)** - Why this exists, what problems it solves, user experience goals
3. **[systemPatterns.md](systemPatterns.md)** - Architecture, design patterns, and technical decisions
4. **[techContext.md](techContext.md)** - Technology stack, dependencies, and constraints
5. **[activeContext.md](activeContext.md)** - Current state, recent work, and immediate context
6. **[progress.md](progress.md)** - What's complete, what's working, and current status

### Key Insights Summary

#### Project Status: ✅ PRODUCTION READY
The framework has reached **production maturity** with all core features implemented, tested, and documented.

#### Core Capabilities
- **Multiple Agent Types**: BaseAgent, Agent, WebSearchAgent, DeepResearchAgent, MultiAgentSystem
- **Rich Tool Ecosystem**: Web search, Google Drive, MCP servers, approval systems, agent handoffs
- **Production Features**: Async-first, error handling, resource management, comprehensive logging
- **Developer Experience**: 3-line agent creation, extensive examples, type safety

#### Architecture Strengths
- **Clean Abstractions**: Abstract base classes with specialized implementations
- **Composition over Inheritance**: Tools as composable components
- **Async-First Design**: All I/O operations are asynchronous for performance
- **Resource Management**: Proper cleanup of external connections (MCP, Google APIs)
- **Error Resilience**: Comprehensive error handling with graceful degradation

#### Integration Capabilities
- **MCP Protocol**: Full Model Context Protocol support for external tools
- **Web Search**: Brave Search API with Firecrawl content extraction
- **Google Drive**: OAuth2 authentication with content extraction (Docs, PDFs, Sheets)
- **Multi-Agent**: Agent coordination with context transfer and handoff patterns

## Quick Reference

### Agent Creation Patterns
```python
# Basic agent
agent = Agent(name="Assistant", description="Helpful AI assistant")

# Web search agent
agent = Agent(enable_web_search=True)

# Google Drive integration
agent = Agent(enable_google_drive=True)

# MCP server integration
agent = Agent(mcp_servers=[{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
}])

# Deep research agent
agent = DeepResearchAgent(
    config=DeepResearchConfig(
        enable_sources=["web", "google_drive"],
        enable_google_drive=True
    )
)
```

### Tool Development Pattern
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
```

### Usage Patterns
```python
# Async (recommended)
response = await agent.run_async("Query")

# Sync wrapper
response = agent.run("Query")

# With cleanup
try:
    response = await agent.run_async("Query")
finally:
    await agent.cleanup()
```

## Framework Components

### Agent Hierarchy
```
BaseAgent (Abstract)
├── Agent (General purpose)
├── WebSearchAgent (Web-focused)
├── DeepResearchAgent (Research-focused)
└── MultiAgentSystem (Orchestration)
```

### Tool Ecosystem
```
Tool (Abstract Base)
├── Web Tools (BraveSearchTool, FirecrawlContentTool)
├── Google Tools (GoogleDriveTool, GoogleDriveContentTool)
├── System Tools (RequestApprovalTool, HandoffTool)
└── MCP Tools (Dynamic wrapper for external servers)
```

### Key Files & Locations
```
src/
├── agents/
│   ├── base.py              # BaseAgent foundation
│   ├── agent.py             # General-purpose Agent
│   ├── web_search.py        # WebSearchAgent
│   ├── deep_research.py     # DeepResearchAgent with citations
│   └── multi_agent_system.py # MultiAgentSystem orchestration
├── tools/
│   ├── base.py              # Tool abstract base class
│   ├── web_search.py        # Brave + Firecrawl tools
│   ├── google_drive.py      # Google Drive integration
│   ├── mcp_tool.py          # MCP server wrapper
│   ├── handoff.py           # Agent handoff tool
│   └── approval.py          # Human approval tool
└── utils/
    ├── connections.py       # MCP connection management
    ├── message_history.py   # Conversation persistence
    └── approval.py          # Approval utilities
```

## Getting Started

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
ANTHROPIC_API_KEY=your_key
BRAVE_API_KEY=your_key        # Optional
FIRECRAWL_API_KEY=your_key    # Optional

# Optional: Google Drive setup
python scripts/setup_google_drive.py
```

### Example Usage
See `examples/` directory for comprehensive examples:
- `basic_web_search.py` - Simple web search
- `deep_research.py` - Advanced research with citations
- `mcp_example.py` - MCP server integration
- `handoff_basics.py` - Multi-agent coordination
- `human_in_the_loop.py` - Approval workflows

### Development Patterns
1. **Start Simple**: Use `Agent` with auto-loaded tools
2. **Add Tools**: Create custom tools inheriting from `Tool`
3. **Specialize**: Use specialized agents for specific domains
4. **Scale**: Multi-agent systems for complex workflows
5. **Integrate**: MCP servers for external tool access

## Technical Highlights

### Performance Optimizations
- **Parallel Tool Execution**: Tools run concurrently by default
- **Lazy MCP Initialization**: Connections established on first use
- **Async-First**: Non-blocking I/O throughout
- **Resource Cleanup**: Proper context management

### Production Features
- **Error Handling**: Comprehensive with graceful degradation
- **Rate Limiting**: Handled by external service SDKs
- **Security**: API key validation, input sanitization
- **Logging**: Verbose mode for debugging
- **Testing**: Async test support with pytest

### Integration Strengths
- **MCP Protocol**: Seamless external tool integration
- **Web Services**: Robust web search and content extraction
- **Google Services**: Full OAuth2 flow with content extraction
- **Multi-Modal**: Text, PDFs, images, structured documents

## Next Steps for Development

### Immediate Opportunities
1. **Custom Agents**: Build domain-specific agents for your use case
2. **Custom Tools**: Integrate with your APIs and services
3. **Multi-Agent Workflows**: Design coordinated agent systems
4. **MCP Servers**: Connect to external tool ecosystems

### Framework Extensions
1. **Additional Integrations**: Slack, Discord, GitHub, databases
2. **Agent Templates**: Pre-configured agents for common patterns
3. **Monitoring**: Metrics and observability integration
4. **CLI Tools**: Command-line interface for operations

This framework provides an excellent foundation for building sophisticated AI agent applications while maintaining clean, maintainable code patterns.

---

*Last Updated: June 10, 2025*
*Status: Production Ready*
*Framework Version: 0.1.0*
