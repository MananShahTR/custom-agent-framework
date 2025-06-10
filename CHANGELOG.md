# Changelog

All notable changes to Storm Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-10

### Added
- **Real-time Streaming Support**: Complete streaming implementation for all agent types
  - `stream` parameter in `run_async()` and `run()` methods for unified interface
  - Real-time streaming responses with incremental text delivery
  - 14 different streaming event types for comprehensive monitoring
  - Backward compatible `stream_async()` method preserved

- **Comprehensive Event System**:
  - `text_delta`: Incremental text content for real-time UI updates
  - `tool_start`/`tools_start`: Tool execution tracking with progress indicators
  - `message_start`/`message_stop`: Full message lifecycle events
  - `stream_event`: Raw Anthropic events for advanced debugging
  - `error` and `max_iterations_reached`: Robust error handling

- **Developer Tools and Examples**:
  - `examples/streaming_example.py`: Interactive streaming demonstrations
  - `examples/streaming_events_showcase.py`: All 14 event types demonstrated
  - `STREAMING_GUIDE.md`: Comprehensive streaming documentation
  - Event filtering and metrics tracking examples
  - Production-ready streaming patterns

- **Production Features**:
  - Non-blocking streaming with tool execution support
  - Multi-iteration streaming flows with progress tracking
  - Memory-efficient event processing
  - Comprehensive error handling during streaming
  - Token usage monitoring through streaming events

### Enhanced
- All agent types now support streaming: `Agent`, `WebSearchAgent`, `DeepResearchAgent`
- Tool execution seamlessly integrated with streaming responses
- Message history management during streaming operations
- Performance optimizations for real-time response delivery

### Technical Details
- **Streaming Architecture**: Event-driven, non-blocking design
- **Event Types**: 14 distinct event types covering all streaming scenarios
- **Performance**: Real-time text delivery with tool execution support
- **Compatibility**: 100% backward compatible with existing code

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
