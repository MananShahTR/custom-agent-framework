"""Comprehensive example showcasing all streaming event types in Storm Agent."""

import asyncio
import json
from typing import Dict, Any
from storm_agent import Agent


class StreamingEventLogger:
    """Logger that captures and displays all streaming events with detailed information."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.events_seen = set()
        self.text_content = ""
        self.tool_inputs = {}
        self.message_usage = None
        
    def log_event(self, event: Dict[str, Any]) -> None:
        """Log a streaming event with detailed information."""
        event_type = event.get("type", "unknown")
        self.events_seen.add(event_type)
        
        if self.verbose:
            print(f"\n📡 EVENT: {event_type}")
            print("-" * 40)
        
        # Handle each event type with specific processing
        if event_type == "stream_event":
            self._handle_stream_event(event)
        elif event_type == "message_start":
            self._handle_message_start(event)
        elif event_type == "text_start":
            self._handle_text_start(event)
        elif event_type == "text_delta":
            self._handle_text_delta(event)
        elif event_type == "tool_start":
            self._handle_tool_start(event)
        elif event_type == "tool_input_delta":
            self._handle_tool_input_delta(event)
        elif event_type == "content_block_stop":
            self._handle_content_block_stop(event)
        elif event_type == "message_delta":
            self._handle_message_delta(event)
        elif event_type == "message_stop":
            self._handle_message_stop(event)
        elif event_type == "tools_start":
            self._handle_tools_start(event)
        elif event_type == "tools_complete":
            self._handle_tools_complete(event)
        elif event_type == "final_response":
            self._handle_final_response(event)
        elif event_type == "error":
            self._handle_error(event)
        elif event_type == "max_iterations_reached":
            self._handle_max_iterations(event)
        else:
            self._handle_unknown_event(event)
        
        if self.verbose:
            print("-" * 40)
    
    def _handle_stream_event(self, event: Dict[str, Any]) -> None:
        """Handle raw Anthropic streaming events."""
        raw_event = event.get("event")
        if raw_event and hasattr(raw_event, 'type'):
            print(f"🔧 Raw Anthropic event: {raw_event.type}")
            if hasattr(raw_event, 'delta') and hasattr(raw_event.delta, 'type'):
                print(f"   Delta type: {raw_event.delta.type}")
        else:
            print("🔧 Raw streaming event (no type info)")
    
    def _handle_message_start(self, event: Dict[str, Any]) -> None:
        """Handle message start events."""
        message = event.get("message", {})
        print(f"🚀 Message started")
        print(f"   Model: {message.get('model', 'unknown')}")
        print(f"   Message ID: {message.get('id', 'unknown')}")
        
        usage = message.get("usage", {})
        if usage:
            print(f"   Input tokens: {usage.get('input_tokens', 0)}")
    
    def _handle_text_start(self, event: Dict[str, Any]) -> None:
        """Handle text content start events."""
        index = event.get("index", 0)
        print(f"📝 Text content started at index {index}")
        if self.verbose:
            print("   (Text will stream in via text_delta events)")
    
    def _handle_text_delta(self, event: Dict[str, Any]) -> None:
        """Handle incremental text content."""
        text = event.get("text", "")
        index = event.get("index", 0)
        self.text_content += text
        
        if self.verbose:
            # Show the text with highlighting
            print(f"📄 Text delta (index {index}): '{text}'")
            print(f"   Total accumulated: '{self.text_content[-50:]}'..." if len(self.text_content) > 50 else f"   Total accumulated: '{self.text_content}'")
        else:
            # For non-verbose mode, just print the text as it comes
            print(text, end="", flush=True)
    
    def _handle_tool_start(self, event: Dict[str, Any]) -> None:
        """Handle tool usage start events."""
        tool_name = event.get("tool_name", "unknown")
        tool_id = event.get("tool_id", "unknown")
        index = event.get("index", 0)
        
        print(f"🔧 Tool started: {tool_name}")
        print(f"   Tool ID: {tool_id}")
        print(f"   Content index: {index}")
        
        # Initialize tool input tracking
        self.tool_inputs[tool_id] = ""
    
    def _handle_tool_input_delta(self, event: Dict[str, Any]) -> None:
        """Handle incremental tool input construction."""
        partial_json = event.get("partial_json", "")
        index = event.get("index", 0)
        
        print(f"⚙️  Tool input delta (index {index}): '{partial_json}'")
        
        # Try to track the building input
        if partial_json:
            print(f"   Building tool input: {partial_json}")
    
    def _handle_content_block_stop(self, event: Dict[str, Any]) -> None:
        """Handle content block completion."""
        index = event.get("index", 0)
        print(f"🛑 Content block stopped at index {index}")
    
    def _handle_message_delta(self, event: Dict[str, Any]) -> None:
        """Handle message-level updates."""
        delta = event.get("delta", {})
        usage = event.get("usage")
        
        print(f"📊 Message delta update")
        if delta:
            print(f"   Delta: {delta}")
        
        if usage:
            self.message_usage = usage
            print(f"   Usage update:")
            if hasattr(usage, 'input_tokens'):
                print(f"     Input tokens: {usage.input_tokens}")
            if hasattr(usage, 'output_tokens'):
                print(f"     Output tokens: {usage.output_tokens}")
            if hasattr(usage, 'cache_creation_input_tokens'):
                print(f"     Cache creation: {usage.cache_creation_input_tokens}")
    
    def _handle_message_stop(self, event: Dict[str, Any]) -> None:
        """Handle message completion."""
        print(f"🏁 Message completed")
        print(f"   Final text length: {len(self.text_content)} characters")
    
    def _handle_tools_start(self, event: Dict[str, Any]) -> None:
        """Handle multiple tools execution start."""
        tool_calls = event.get("tool_calls", [])
        iteration = event.get("iteration", 1)
        
        print(f"🛠️  Tools execution started (iteration {iteration})")
        print(f"   Number of tools: {len(tool_calls)}")
        
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"   {i}. {tool_call.name}: {tool_call.input}")
    
    def _handle_tools_complete(self, event: Dict[str, Any]) -> None:
        """Handle tools execution completion."""
        tool_results = event.get("tool_results", [])
        iteration = event.get("iteration", 1)
        
        print(f"✅ Tools execution completed (iteration {iteration})")
        print(f"   Number of results: {len(tool_results)}")
        
        for i, result in enumerate(tool_results, 1):
            content = result.get("content", "")
            content_preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   {i}. Result preview: {content_preview}")
    
    def _handle_final_response(self, event: Dict[str, Any]) -> None:
        """Handle final response availability."""
        response = event.get("response")
        print(f"🎯 Final response available")
        
        if response:
            print(f"   Response ID: {response.id}")
            print(f"   Model: {response.model}")
            print(f"   Stop reason: {response.stop_reason}")
            if hasattr(response, 'usage'):
                print(f"   Final usage: {response.usage}")
    
    def _handle_error(self, event: Dict[str, Any]) -> None:
        """Handle error events."""
        error = event.get("error", "Unknown error")
        iteration = event.get("iteration", "unknown")
        
        print(f"❌ ERROR occurred")
        print(f"   Error: {error}")
        print(f"   Iteration: {iteration}")
    
    def _handle_max_iterations(self, event: Dict[str, Any]) -> None:
        """Handle max iterations reached."""
        max_iterations = event.get("max_iterations", "unknown")
        print(f"⏳ Maximum iterations reached: {max_iterations}")
    
    def _handle_unknown_event(self, event: Dict[str, Any]) -> None:
        """Handle unknown event types."""
        print(f"❓ Unknown event type")
        print(f"   Event data: {json.dumps(event, indent=2, default=str)}")
    
    def print_summary(self) -> None:
        """Print a summary of all events seen."""
        print("\n" + "=" * 60)
        print("📋 STREAMING EVENTS SUMMARY")
        print("=" * 60)
        print(f"Total event types seen: {len(self.events_seen)}")
        print(f"Events: {', '.join(sorted(self.events_seen))}")
        print(f"Final text content length: {len(self.text_content)} characters")
        
        if self.message_usage:
            print(f"Final token usage: {self.message_usage}")
        
        print("\n🎓 Event Type Explanations:")
        explanations = {
            "stream_event": "Raw Anthropic streaming event (for advanced debugging)",
            "message_start": "Beginning of Claude's response message",
            "text_start": "Start of a text content block",
            "text_delta": "Incremental text as it's generated (main content)",
            "tool_start": "A tool is about to be used",
            "tool_input_delta": "Tool parameters being constructed incrementally",
            "content_block_stop": "End of a content block (text or tool)",
            "message_delta": "Message-level updates (usage info, etc.)",
            "message_stop": "End of Claude's response message",
            "tools_start": "Multiple tools beginning execution",
            "tools_complete": "Tool execution finished with results",
            "final_response": "Complete response object is available",
            "error": "An error occurred during processing",
            "max_iterations_reached": "Agent hit its iteration limit"
        }
        
        for event_type in sorted(self.events_seen):
            if event_type in explanations:
                print(f"  • {event_type}: {explanations[event_type]}")
        
        missing_events = set(explanations.keys()) - self.events_seen
        if missing_events:
            print(f"\n📝 Events not seen in this session: {', '.join(sorted(missing_events))}")


async def showcase_all_events():
    """Demonstrate all possible streaming event types."""
    print("🌊 Storm Agent Streaming Events Showcase")
    print("=" * 60)
    print("This example will trigger various streaming events to show you all event types.\n")
    
    # Create agent with tools to trigger tool-related events
    agent = Agent(
        name="EventShowcaseBot",
        description="An agent for demonstrating all streaming event types",
        enable_web_search=True,  # This will trigger tool events
        max_iterations=3,  # Limit to potentially trigger max_iterations_reached
        verbose=True
    )
    
    logger = StreamingEventLogger(verbose=True)
    
    try:
        # Example 1: Simple text response (fewer events)
        print("\n🎭 DEMO 1: Simple conversation (minimal events)")
        print("-" * 50)
        
        query1 = "Hello! Please write a very brief greeting."
        print(f"User: {query1}")
        
        async for event in await agent.run_async(query1, stream=True):
            logger.log_event(event)
            if event.get("type") == "final_response":
                break
        
        # Reset for next demo
        logger_detailed = StreamingEventLogger(verbose=True)
        
        print("\n\n🎭 DEMO 2: Complex query with tools (many events)")
        print("-" * 50)
        
        query2 = "Please search for recent news about artificial intelligence and summarize what you find."
        print(f"User: {query2}")
        
        async for event in await agent.run_async(query2, stream=True):
            logger_detailed.log_event(event)
            if event.get("type") == "final_response":
                break
        
        # Example 3: Trigger error (optional - would need special setup)
        print("\n\n🎭 DEMO 3: Event summary")
        print("-" * 50)
        logger_detailed.print_summary()
        
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        logger.log_event({"type": "error", "error": str(e)})
    
    finally:
        await agent.cleanup()


async def minimal_event_handler():
    """Show a minimal way to handle the most important events."""
    print("\n\n🎯 MINIMAL EVENT HANDLING EXAMPLE")
    print("=" * 60)
    print("This shows how to handle just the essential events for most applications.\n")
    
    agent = Agent(
        name="MinimalBot",
        description="A bot for minimal event handling demo",
        enable_web_search=True
    )
    
    try:
        query = "Search for the latest news about Python programming language"
        print(f"User: {query}")
        print("Assistant: ", end="", flush=True)
        
        async for event in await agent.run_async(query, stream=True):
            event_type = event.get("type")
            
            # Handle only the essential events
            if event_type == "text_delta":
                # Stream text as it comes
                print(event.get("text", ""), end="", flush=True)
            
            elif event_type == "tools_start":
                # Show when tools are running
                tool_calls = event.get("tool_calls", [])
                print(f"\n[🔧 Using {len(tool_calls)} tools...]")
            
            elif event_type == "tools_complete":
                # Resume text display after tools
                print("Assistant (continued): ", end="", flush=True)
            
            elif event_type == "error":
                # Handle errors
                error = event.get("error", "Unknown error")
                print(f"\n❌ Error: {error}")
                break
            
            elif event_type == "final_response":
                # Response is complete
                print("\n✨ Done!")
                break
            
            # Ignore all other event types for simplicity
    
    finally:
        await agent.cleanup()


async def event_filtering_example():
    """Show how to filter and process specific event types."""
    print("\n\n🔍 EVENT FILTERING EXAMPLE")
    print("=" * 60)
    print("This shows how to filter for specific event types you care about.\n")
    
    agent = Agent(
        name="FilterBot",
        description="A bot for event filtering demo",
        enable_web_search=True
    )
    
    # Track specific metrics
    metrics = {
        "text_chunks": 0,
        "tools_used": 0,
        "total_chars": 0,
        "token_usage": None
    }
    
    try:
        query = "What are the benefits of streaming responses in AI applications?"
        print(f"User: {query}")
        
        async for event in await agent.run_async(query, stream=True):
            event_type = event.get("type")
            
            # Filter for text events
            if event_type == "text_delta":
                text = event.get("text", "")
                metrics["text_chunks"] += 1
                metrics["total_chars"] += len(text)
                print(text, end="", flush=True)
            
            # Filter for tool events
            elif event_type == "tools_start":
                tool_calls = event.get("tool_calls", [])
                metrics["tools_used"] += len(tool_calls)
                print(f"\n[Tools: {', '.join(t.name for t in tool_calls)}]")
            
            # Filter for usage information
            elif event_type == "message_delta":
                usage = event.get("usage")
                if usage:
                    metrics["token_usage"] = usage
            
            # Filter for completion
            elif event_type == "final_response":
                print(f"\n\n📊 Session Metrics:")
                print(f"   Text chunks received: {metrics['text_chunks']}")
                print(f"   Total characters: {metrics['total_chars']}")
                print(f"   Tools used: {metrics['tools_used']}")
                if metrics['token_usage']:
                    print(f"   Token usage: {metrics['token_usage']}")
                break
    
    finally:
        await agent.cleanup()


async def main():
    """Run all the streaming event examples."""
    await showcase_all_events()
    await minimal_event_handler()
    await event_filtering_example()
    
    print("\n" + "=" * 60)
    print("🎓 SUMMARY")
    print("=" * 60)
    print("You've now seen all the streaming event types and different ways to handle them:")
    print("1. Comprehensive logging (for debugging/monitoring)")
    print("2. Minimal essential handling (for most applications)")
    print("3. Selective filtering (for specific metrics/features)")
    print("\nChoose the approach that best fits your application's needs!")


if __name__ == "__main__":
    asyncio.run(main()) 