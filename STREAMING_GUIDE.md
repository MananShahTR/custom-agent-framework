# Storm Agent Streaming Guide

Storm Agent now supports real-time streaming responses for better user experience.

## Quick Start

### Async Streaming
```python
import asyncio
from storm_agent import Agent

async def main():
    agent = Agent(name="StreamingBot", enable_web_search=True)
    
    # Stream the response
    async for event in await agent.run_async("Tell me about AI", stream=True):
        if event["type"] == "text_delta":
            print(event["text"], end="", flush=True)
        elif event["type"] == "final_response":
            break
    
    await agent.cleanup()

asyncio.run(main())
```

### Sync Streaming
```python
from storm_agent import Agent

agent = Agent(name="StreamingBot")

# Stream synchronously
for event in agent.run("Write a poem", stream=True):
    if event["type"] == "text_delta":
        print(event["text"], end="", flush=True)
```

### Traditional Mode (Non-Streaming)
```python
agent = Agent(name="RegularBot")
response = agent.run("Hello", stream=False)  # Default is stream=False
print(response.content[0].text)
```

## Event Types

Storm Agent emits various event types during streaming:

### Core Events
- `text_delta`: Incremental text content (most important for UI)
- `text_start`: Beginning of text content block
- `final_response`: Complete response is ready

### Tool Events  
- `tool_start`: A tool is about to be used
- `tools_start`: Multiple tools beginning execution
- `tools_complete`: Tool execution finished with results
- `tool_input_delta`: Tool parameters being constructed incrementally

### Message Events
- `message_start`: Beginning of Claude's response message
- `message_delta`: Message-level updates (usage info, etc.)
- `message_stop`: End of Claude's response message
- `content_block_stop`: End of a content block

### Control Events
- `stream_event`: Raw Anthropic streaming event (advanced debugging)
- `error`: An error occurred during processing
- `max_iterations_reached`: Agent hit its iteration limit

## Examples

### Basic Usage
See `examples/streaming_example.py` for comprehensive examples including:
- Interactive chat
- Tool usage with streaming
- Error handling
- Performance comparisons

### All Event Types Showcase
See `examples/streaming_events_showcase.py` for a detailed demonstration of:
- **All possible streaming event types**
- **Comprehensive event logging**
- **Minimal essential event handling**
- **Event filtering and metrics tracking**

Run examples:
```bash
# Basic streaming examples
python examples/streaming_example.py

# Comprehensive event showcase  
python examples/streaming_events_showcase.py

# Interactive mode only
python examples/streaming_example.py interactive
```

## Best Practices

### For Chat Applications
```python
async for event in await agent.run_async(query, stream=True):
    if event["type"] == "text_delta":
        # Update UI with new text
        ui.append_text(event["text"])
    elif event["type"] == "tools_start":
        # Show loading indicator
        ui.show_loading("Using tools...")
    elif event["type"] == "final_response":
        # Hide loading, response complete
        ui.hide_loading()
        break
```

### For Monitoring/Logging
```python
async for event in await agent.run_async(query, stream=True):
    if event["type"] == "message_delta":
        # Track token usage
        usage = event.get("usage")
        if usage:
            monitor.log_tokens(usage)
    elif event["type"] == "tools_start":
        # Log tool usage
        tools = event.get("tool_calls", [])
        monitor.log_tools([t.name for t in tools])
``` 