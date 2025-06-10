# MCP (Model Context Protocol) Integration

This agent framework now supports **MCP (Model Context Protocol)** servers, allowing you to connect external tools and services to your AI agents seamlessly.

## What is MCP?

MCP is a protocol that enables AI applications to connect to external data sources and tools through standardized server interfaces. This allows agents to:

- Access file systems
- Query databases  
- Interact with APIs
- Use custom business logic
- And much more!

## Quick Start

### 1. Install MCP Dependencies

```bash
pip install mcp
```

### 2. Basic Usage

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

# Create agent with MCP tools
agent = Agent(
    name="My Agent",
    description="An agent with file system access",
    mcp_servers=mcp_servers,
    verbose=True
)

# Use the agent - MCP tools are automatically available
response = await agent.run_async("List the files in my project directory")

# Clean up when done
await agent.cleanup()
```

## MCP Server Types

### STDIO Servers
Connect to servers that communicate via standard input/output:

```python
{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    "env": {"CUSTOM_VAR": "value"}
}
```

### SSE (Server-Sent Events) Servers
Connect to HTTP-based servers:

```python
{
    "type": "sse",
    "url": "http://localhost:8000/sse",
    "headers": {
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    }
}
```

## Popular MCP Servers

### File System Access
```python
{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
    "env": {}
}
```

### SQLite Database
```python
{
    "type": "stdio",
    "command": "npx", 
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
    "env": {}
}
```

### GitHub Integration
```python
{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"
    }
}
```

### Google Drive
```python
{
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-gdrive"],
    "env": {}
}
```

## Architecture

### How It Works

1. **Initialization**: When you create an agent with `mcp_servers`, the framework stores the configuration
2. **First Use**: On the first `run_async()` call, MCP connections are established automatically
3. **Tool Loading**: Available tools are loaded from each MCP server and added to the agent
4. **Usage**: MCP tools work just like regular tools - Claude can call them during conversations
5. **Cleanup**: Call `agent.cleanup()` to properly close MCP connections

### Key Components

- **`MCPConnection`**: Abstract base for MCP server connections
- **`MCPConnectionStdio`**: STDIO-based connections  
- **`MCPConnectionSSE`**: HTTP SSE-based connections
- **`MCPTool`**: Wrapper that makes MCP server tools available to Claude
- **`setup_mcp_connections()`**: Utility to establish connections and load tools

## Advanced Usage

### Multiple MCP Servers
```python
mcp_servers = [
    # File system access
    {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"],
        "env": {}
    },
    # Database access
    {
        "type": "stdio", 
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", "/data/app.db"],
        "env": {}
    },
    # Custom HTTP service
    {
        "type": "sse",
        "url": "http://localhost:8000/sse",
        "headers": {"Authorization": "Bearer api-key"}
    }
]

agent = Agent(
    name="Multi-Tool Agent",
    mcp_servers=mcp_servers,
    verbose=True
)
```

### Combining with Regular Tools
```python
from src.tools import BraveSearchTool

# Regular tools
regular_tools = [BraveSearchTool()]

# MCP servers  
mcp_servers = [
    {
        "type": "stdio",
        "command": "npx", 
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "env": {}
    }
]

# Agent gets both regular tools AND MCP tools
agent = Agent(
    name="Hybrid Agent",
    tools=regular_tools,           # Regular tools
    mcp_servers=mcp_servers,       # MCP tools
    enable_web_search=True,        # Auto-loaded tools
    verbose=True
)
```

### Error Handling
```python
agent = Agent(
    name="Robust Agent",
    mcp_servers=mcp_servers,
    verbose=True  # Shows MCP setup errors
)

try:
    response = await agent.run_async("Your request")
finally:
    # Always clean up MCP connections
    await agent.cleanup()
```

## Implementation Details

### Following Anthropic Quickstarts Pattern

This implementation closely follows the [Anthropic quickstarts MCP pattern](https://github.com/anthropics/anthropic-quickstarts/tree/main/agents):

1. **Connection Management**: Uses `AsyncExitStack` for proper resource cleanup
2. **Tool Wrapping**: MCP server tools are wrapped as `MCPTool` instances
3. **Error Handling**: Graceful handling of MCP setup failures
4. **Lifecycle Management**: Automatic connection setup and cleanup

### Key Differences from Quickstarts

- **Persistent Tools**: MCP tools are added permanently to the agent (not temporarily)
- **Simpler API**: No separate `_run_with_mcp` - MCP tools are just part of the agent
- **Automatic Setup**: MCP connections established on first use
- **Cleanup Method**: Explicit `cleanup()` method for resource management

## Troubleshooting

### Common Issues

**MCP dependencies not installed:**
```bash
pip install mcp
```

**MCP server not found:**
```bash
# Install the specific MCP server
npx -y @modelcontextprotocol/server-filesystem --help
```

**Permission errors:**
- Check file/directory permissions for filesystem servers
- Verify API tokens for authenticated servers

**Connection timeouts:**
- Ensure MCP servers are responsive
- Check network connectivity for SSE servers

### Debugging

Enable verbose mode to see MCP setup details:
```python
agent = Agent(
    name="Debug Agent",
    mcp_servers=mcp_servers,
    verbose=True  # Shows MCP connection details
)
```

## Best Practices

1. **Always call cleanup()**: Properly close MCP connections
2. **Use verbose mode**: During development to see what tools are loaded
3. **Handle errors gracefully**: MCP servers can fail - design for resilience  
4. **Limit scope**: Only give MCP servers access to necessary directories/resources
5. **Secure credentials**: Use environment variables for API tokens and secrets

## Examples

See `examples/mcp_example.py` for a complete working example demonstrating MCP integration.

---

*This integration is based on the [Anthropic MCP quickstarts](https://github.com/anthropics/anthropic-quickstarts/tree/main/agents) and follows the same patterns for reliability and compatibility.* 