# Changelog

All notable changes to Storm Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-10

### Added
- Initial release of Storm Agent framework
- **Core Agent System**:
  - `BaseAgent`: Abstract foundation for all agent types
  - `Agent`: General-purpose agent with flexible tool composition
  - `WebSearchAgent`: Specialized agent for web research tasks
  - `DeepResearchAgent`: Advanced research agent with citations
  - `MultiAgentSystem`: Multi-agent coordination and orchestration

- **Comprehensive Tool Ecosystem**:
  - Web tools: `BraveSearchTool`, `FirecrawlContentTool`
  - Google Drive tools: `GoogleDriveTool`, `GoogleDriveContentTool`
  - System tools: `RequestApprovalTool`, `HandoffTool`
  - MCP integration: `MCPTool` for external service connections

- **Production Features**:
  - Async-first architecture with parallel tool execution
  - Comprehensive error handling and graceful degradation
  - Resource management with automatic cleanup
  - Human-in-the-loop approval mechanisms
  - Persistent message history management

- **Integration Capabilities**:
  - Model Context Protocol (MCP) support for external tools
  - Google Drive OAuth2 authentication and content extraction
  - Web search with Brave Search API and Firecrawl
  - Citation system for research tasks

- **Developer Experience**:
  - Clean, intuitive API design
  - Comprehensive type hints throughout
  - Command-line interface (`storm-agent` CLI)
  - Extensive examples and documentation
  - PyPI distribution ready

- **Quality Assurance**:
  - Comprehensive test suite with async support
  - Code quality tools (Black, Flake8, MyPy)
  - Pre-commit hooks configuration
  - CI/CD pipeline ready

### Technical Details
- **Python Support**: 3.9+
- **Core Dependencies**: anthropic, mcp, requests, python-dotenv
- **Optional Dependencies**: Google APIs, web scraping tools
- **Architecture**: Modular, composition-based design
- **Performance**: Parallel tool execution, non-blocking I/O

### Documentation
- Complete README with installation and usage examples
- API documentation with type hints
- MCP integration guide
- Citation system documentation
- Contributing guidelines

[1.0.0]: https://github.com/storm-agent/storm-agent/releases/tag/v1.0.0
