"""Example demonstrating streaming support in Storm Agent."""

import asyncio
import sys
from storm_agent import Agent


def print_streaming_event(event):
    """Print streaming events in a user-friendly way."""
    event_type = event.get("type", "unknown")
    
    if event_type == "text_delta":
        # Print text as it streams in
        text = event.get("text", "")
        print(text, end="", flush=True)
    
    elif event_type == "text_start":
        print("\n🤖 Assistant: ", end="", flush=True)
    
    elif event_type == "tool_start":
        tool_name = event.get("tool_name", "unknown")
        print(f"\n🔧 Using tool: {tool_name}")
    
    elif event_type == "tool_input_delta":
        # Show tool input as it's being constructed
        partial_json = event.get("partial_json", "")
        if partial_json:
            print(f"   Building input: {partial_json}", end="", flush=True)
    
    elif event_type == "tools_start":
        tool_calls = event.get("tool_calls", [])
        iteration = event.get("iteration", 1)
        print(f"\n🛠️  Executing {len(tool_calls)} tool(s) (iteration {iteration})...")
        for tool_call in tool_calls:
            print(f"   - {tool_call.name}: {tool_call.input}")
    
    elif event_type == "tools_complete":
        iteration = event.get("iteration", 1)
        print(f"✅ Tools completed (iteration {iteration})")
    
    elif event_type == "final_response":
        print("\n\n✨ Streaming completed!")
    
    elif event_type == "error":
        error = event.get("error", "Unknown error")
        print(f"\n❌ Error: {error}")
    
    elif event_type == "max_iterations_reached":
        max_iter = event.get("max_iterations", "unknown")
        print(f"\n⚠️ Max iterations ({max_iter}) reached")


async def async_streaming_example():
    """Demonstrate async streaming with an agent."""
    print("🚀 Async Streaming Example")
    print("=" * 50)
    
    # Create an agent with web search capabilities
    agent = Agent(
        name="StreamingBot",
        description="A streaming assistant that can search the web",
        enable_web_search=True,
        verbose=True
    )
    
    try:
        # Example 1: Simple conversation (no tools)
        print("\n📝 Example 1: Simple conversation")
        print("-" * 30)
        
        query = "Hello! Can you tell me about the benefits of streaming in AI applications?"
        print(f"User: {query}")
        
        # Stream the response
        async for event in await agent.run_async(query, stream=True):
            print_streaming_event(event)
        
        print("\n" + "=" * 50)
        
        # Example 2: Query that will use tools
        print("\n🔍 Example 2: Web search query")
        print("-" * 30)
        
        query = "What are the latest developments in Claude AI from Anthropic in 2024?"
        print(f"User: {query}")
        
        # Stream the response
        async for event in await agent.run_async(query, stream=True):
            print_streaming_event(event)
        
        print("\n" + "=" * 50)
        
        # Example 3: Compare with non-streaming
        print("\n⚡ Example 3: Non-streaming for comparison")
        print("-" * 40)
        
        query = "Explain streaming vs non-streaming briefly"
        print(f"User: {query}")
        
        # Non-streaming response
        response = await agent.run_async(query, stream=False)
        print("🤖 Assistant (non-streaming):")
        if hasattr(response, 'content'):
            for content in response.content:
                if hasattr(content, 'text'):
                    print(content.text)
        
    finally:
        # Clean up agent resources
        await agent.cleanup()


def sync_streaming_example():
    """Demonstrate synchronous streaming with an agent."""
    print("\n🔄 Sync Streaming Example")
    print("=" * 50)
    
    # Create a simple agent without web search for faster demo
    agent = Agent(
        name="SyncStreamingBot",
        description="A synchronous streaming assistant",
        verbose=True
    )
    
    query = "Write a short poem about streaming data in real-time"
    print(f"User: {query}")
    
    # Stream the response synchronously
    for event in agent.run(query, stream=True):
        print_streaming_event(event)
    
    print("\n" + "=" * 50)


async def interactive_streaming_demo():
    """Interactive demo where user can type queries and see streaming responses."""
    print("\n💬 Interactive Streaming Demo")
    print("=" * 50)
    print("Type your queries and see streaming responses!")
    print("Type 'exit' to quit, 'non-stream' to toggle non-streaming mode")
    print("-" * 50)
    
    agent = Agent(
        name="InteractiveBot",
        description="An interactive streaming assistant",
        enable_web_search=True,
        verbose=False  # Less verbose for interactive use
    )
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("\n💭 You: ").strip()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'non-stream':
                # Demonstrate non-streaming mode
                user_input = input("💭 You (non-streaming): ").strip()
                print("🤖 Assistant (non-streaming):")
                response = await agent.run_async(user_input, stream=False)
                if hasattr(response, 'content'):
                    for content in response.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                continue
            
            if not user_input:
                continue
            
            # Stream the response
            print("🤖 Assistant: ", end="", flush=True)
            text_started = False
            
            async for event in await agent.run_async(user_input, stream=True):
                event_type = event.get("type", "unknown")
                
                if event_type == "text_delta":
                    if not text_started:
                        text_started = True
                    text = event.get("text", "")
                    print(text, end="", flush=True)
                
                elif event_type == "tools_start":
                    tool_calls = event.get("tool_calls", [])
                    print(f"\n   🔧 Using {len(tool_calls)} tool(s)...")
                
                elif event_type == "final_response":
                    if text_started:
                        print()  # New line after streaming text
                    break
    
    finally:
        await agent.cleanup()


async def main():
    """Run all the streaming examples."""
    print("🌊 Storm Agent Streaming Examples")
    print("=" * 60)
    
    # Run async streaming example
    await async_streaming_example()
    
    # Run sync streaming example
    sync_streaming_example()
    
    # Ask if user wants interactive demo
    try:
        choice = input("\n🎮 Would you like to try the interactive demo? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            await interactive_streaming_demo()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    # Handle different ways of running the script
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            asyncio.run(interactive_streaming_demo())
        elif sys.argv[1] == "async":
            asyncio.run(async_streaming_example())
        elif sys.argv[1] == "sync":
            sync_streaming_example()
        else:
            print("Usage: python streaming_example.py [interactive|async|sync]")
    else:
        # Run all examples by default
        asyncio.run(main()) 