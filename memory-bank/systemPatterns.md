# System Patterns: Custom AI Agents Framework

## Architecture Overview

### Core Design Philosophy
- **Clean Abstractions**: Simple interfaces hiding complex implementations
- **Composition over Inheritance**: Tools and capabilities as composable components
- **Async-First**: All I/O operations are asynchronous for performance
- **Resource Management**: Proper cleanup of external connections (MCP, Google APIs)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
├─────────────────────────────────────────────────────────────┤
│                    Agent Layer                              │
│  ┌─────────────────┬─────────────────┬─────────────────────┐ │
│  │   BaseAgent     │   Agent         │  DeepResearchAgent  │ │
│  │   (Abstract)    │   (General)     │   (Specialized)     │ │
│  └─────────────────┴─────────────────┴─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Tool Layer                               │
│  ┌─────────────────┬─────────────────┬─────────────────────┐ │
│  │   Tool (Base)   │  BraveSearch    │   GoogleDrive       │ │
│  │                 │  Firecrawl      │   MCP Tools         │ │
│  └─────────────────┴─────────────────┴─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   External Services                         │
│  ┌─────────────────┬─────────────────┬─────────────────────┐ │
│  │  Anthropic API  │   Web Services  │   MCP Servers       │ │
│  │    (Claude)     │  (Brave, etc.)  │   (File, DB, etc.)  │ │
│  └─────────────────┴─────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. **Abstract Base Classes**
```python
class BaseAgent(ABC):
    @abstractmethod
    async def run_async(self, user_input: str, **kwargs) -> Any:
        pass
    
class Tool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass
```

**Benefits:**
- Consistent interface across all agents/tools
- Enforces required method implementation
- Enables polymorphic usage

### 2. **Configuration Objects**
```python
@dataclass
class ModelConfig:
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 1.0
```

**Benefits:**
- Centralized configuration management
- Type safety with dataclasses
- Easy configuration inheritance

### 3. **Dependency Injection**
```python
def __init__(self, client: Optional[Anthropic] = None):
    self.client = client or Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

**Benefits:**
- Testability (mock injection)
- Flexibility (custom clients)
- Environment-aware defaults

### 4. **Tool Registry Pattern**
```python
self.tool_dict = {tool.name: tool for tool in self.tools}
```

**Benefits:**
- Fast tool lookup by name
- Dynamic tool addition (MCP)
- Type-safe tool execution

### 5. **Async Context Management**
```python
async def _ensure_mcp_setup(self):
    self._mcp_stack = AsyncExitStack()
    await self._mcp_stack.__aenter__()
    # Setup MCP connections
```

**Benefits:**
- Proper resource cleanup
- Exception-safe resource management
- Async-compatible context handling

## Component Relationships

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
├── Web Tools
│   ├── BraveSearchTool
│   └── FirecrawlContentTool
├── Google Tools
│   ├── GoogleDriveTool
│   └── GoogleDriveContentTool
├── System Tools
│   ├── RequestApprovalTool
│   └── HandoffTool
└── MCP Tools
    └── MCPTool (Dynamic wrapper)
```

### Utility Modules
```
utils/
├── connections.py     # MCP connection management
├── message_history.py # Conversation persistence
└── approval.py        # Human-in-the-loop approval
```

## Critical Implementation Paths

### 1. **Agent Execution Flow**
```python
async def run_async(self, user_input: str) -> Any:
    await self._ensure_mcp_setup()  # Lazy MCP initialization
    
    while True:  # Agent loop
        response = await self.client.messages.create(...)  # Claude API
        
        if no_tool_calls:
            return formatted_response
        
        tool_results = await self.execute_tool_calls(...)  # Parallel tool execution
        messages.extend(tool_results)  # Add results to conversation
```

### 2. **Tool Execution Pattern**
```python
async def execute_tool_calls(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
    async def _execute_single_tool(call: Any) -> Dict[str, Any]:
        tool = self.tool_dict[call.name]
        result = await tool.execute(**call.input)
        return {"tool_use_id": call.id, "content": result}
    
    # Parallel execution for performance
    tasks = [_execute_single_tool(call) for call in tool_calls]
    return await asyncio.gather(*tasks)
```

### 3. **MCP Integration Pattern**
```python
async def setup_mcp_connections(servers: List[Dict], stack: AsyncExitStack) -> List[Tool]:
    connections = []
    for server_config in servers:
        if server_config["type"] == "stdio":
            connection = MCPConnectionStdio(...)
        elif server_config["type"] == "sse":
            connection = MCPConnectionSSE(...)
        
        await stack.enter_async_context(connection)
        connections.append(connection)
    
    # Convert MCP tools to framework tools
    return [MCPTool(tool_info) for connection in connections 
            for tool_info in connection.list_tools()]
```

## Design Decisions

### 1. **Async-First Architecture**
**Decision**: All I/O operations are async
**Rationale**: 
- Better performance for tool-heavy agents
- Parallel tool execution
- Non-blocking web requests

### 2. **Tool Composition over Agent Inheritance**
**Decision**: Agents compose tools rather than inheriting capabilities
**Rationale**:
- More flexible than deep inheritance hierarchies
- Easy to add/remove capabilities
- Better separation of concerns

### 3. **Lazy MCP Initialization**
**Decision**: MCP connections established on first use, not construction
**Rationale**:
- Faster agent creation
- Avoid connection overhead for simple queries
- Better error handling (connection errors at runtime, not startup)

### 4. **Dictionary-Based Tool Registry**
**Decision**: Use dict for tool lookup instead of linear search
**Rationale**:
- O(1) tool lookup performance
- Easy to add/remove tools dynamically
- Clean API for tool management

### 5. **Separate Configuration Objects**
**Decision**: Use dataclasses for configuration instead of kwargs
**Rationale**:
- Type safety and IDE support
- Clear separation of concerns
- Easy to extend and validate

### 6. **Resource Cleanup with AsyncExitStack**
**Decision**: Use AsyncExitStack for MCP connection cleanup
**Rationale**:
- Guaranteed cleanup even on exceptions
- Async-compatible resource management
- Follows Python context manager patterns

These patterns ensure the framework is maintainable, extensible, and production-ready while keeping the API simple for end users.
