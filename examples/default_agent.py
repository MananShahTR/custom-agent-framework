"""Example of using the default configurable Agent."""

import asyncio
import sys
import os

# Add parent directory to Python path to import src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storm_agentagents import Agent, ModelConfig


async def simple_text_assistant():
    """Example 1: Simple text-only assistant."""
    print("🤖 Example 1: Simple Text Assistant")
    print("=" * 50)
    
    agent = Agent(
        name="Assistant",
        system_prompt="You are a helpful assistant that answers questions clearly and concisely.",
        verbose=True
    )
    
    response = await agent.run_async("What are the benefits of exercise?")
    
    # Print the text response
    for content in response.content:
        if hasattr(content, 'text'):
            print(content.text)


async def web_enabled_assistant():
    """Example 2: Web-enabled assistant."""
    print("\n\n🌐 Example 2: Web-Enabled Assistant")
    print("=" * 50)
    
    agent = Agent(
        name="WebAssistant",
        description="An AI assistant with web search capabilities",
        enable_web_search=True,  # Includes both search and content extraction tools
        verbose=True
    )
    
    response = await agent.run_async(
        "What are the latest developments in AI from this week? Please search for recent news."
    )
    
    # Print the response
    for content in response.content:
        if hasattr(content, 'text'):
            print(content.text)


async def custom_tools_assistant():
    """Example 3: Assistant with custom tools."""
    print("\n\n🔧 Example 3: Custom Tools Assistant")
    print("=" * 50)
    
    # For this example, we'll use Google Drive tool if available
    try:
        from storm_agenttools.google_drive import GoogleDriveTool
        google_drive_tool = GoogleDriveTool()
        custom_tools = [google_drive_tool]
        
        agent = Agent(
            name="ResearchAssistant",
            description="An AI assistant with Google Drive and web search capabilities",
            enable_web_search=True,
            tools=custom_tools,
            verbose=True
        )
        
        response = await agent.run_async(
            "Search for documents about 'machine learning' and summarize what you find."
        )
        
        # Print the response
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
                
    except ImportError:
        print("⚠️ Google Drive tools not available, skipping custom tools example")


async def advanced_configuration():
    """Example 4: Advanced configuration."""
    print("\n\n⚙️ Example 4: Advanced Configuration")
    print("=" * 50)
    
    # Custom model configuration
    custom_config = ModelConfig(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        temperature=0.7
    )
    
    agent = Agent(
        name="AdvancedAssistant",
        description="A sophisticated AI assistant with custom configuration",
        system_prompt="""You are an advanced AI assistant designed to provide detailed, analytical responses.
        
You should:
- Think step by step through complex problems
- Provide well-structured, comprehensive answers
- Use tools when they would be helpful
- Be precise and thorough in your analysis""",
        enable_web_search=True,
        config=custom_config,
        max_iterations=15,
        parallel_tools=True,
        verbose=True,
        message_params={"metadata": {"session_id": "advanced_example"}}
    )
    
    response = await agent.run_async(
        "Analyze the current state of renewable energy adoption globally. "
        "What are the main trends, challenges, and opportunities?"
    )
    
    # Print the response
    for content in response.content:
        if hasattr(content, 'text'):
            print(content.text)
    
    # Show agent summary
    print("\n📊 Agent Summary:")
    summary = agent.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


async def stateless_assistant():
    """Example 5: Stateless assistant (no message history)."""
    print("\n\n💬 Example 5: Stateless Assistant")
    print("=" * 50)
    
    agent = Agent(
        name="StatelessAssistant",
        description="An assistant that doesn't maintain conversation history",
        enable_message_history=False,
        verbose=True
    )
    
    # Each call is independent
    response1 = await agent.run_async("My name is Alice. What's the weather like?")
    response2 = await agent.run_async("What's my name?")  # Won't remember Alice
    
    print("First response:")
    for content in response1.content:
        if hasattr(content, 'text'):
            print(content.text)
    
    print("\nSecond response (won't remember the name):")
    for content in response2.content:
        if hasattr(content, 'text'):
            print(content.text)


async def conversation_example():
    """Example 6: Multi-turn conversation."""
    print("\n\n💭 Example 6: Multi-turn Conversation")
    print("=" * 50)
    
    agent = Agent(
        name="ConversationAssistant",
        description="An assistant for extended conversations",
        enable_web_search=True,
        verbose=True
    )
    
    # First turn
    print("User: Tell me about Python programming")
    response1 = await agent.run_async("Tell me about Python programming")
    for content in response1.content:
        if hasattr(content, 'text'):
            print(f"Assistant: {content.text}")
    
    # Second turn - should remember context
    print("\nUser: What are its main advantages?")
    response2 = await agent.run_async("What are its main advantages?")
    for content in response2.content:
        if hasattr(content, 'text'):
            print(f"Assistant: {content.text}")
    
    # Third turn - ask for current information
    print("\nUser: What are the latest Python updates?")
    response3 = await agent.run_async("What are the latest Python updates?")
    for content in response3.content:
        if hasattr(content, 'text'):
            print(f"Assistant: {content.text}")


async def main():
    """Run all examples."""
    print("🚀 AI Agents Framework - Default Agent Examples")
    print("=" * 80)
    
    try:
        # Example 1: Simple text assistant
        # await simple_text_assistant()
        
        # Example 2: Web-enabled assistant
        await web_enabled_assistant()
        
        # # Example 3: Custom tools assistant
        # await custom_tools_assistant()
        
        # # Example 4: Advanced configuration
        # await advanced_configuration()
        
        # # Example 5: Stateless assistant
        # await stateless_assistant()
        
        # # Example 6: Multi-turn conversation
        # await conversation_example()
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure you have:")
        print("1. ANTHROPIC_API_KEY set in your environment")
        print("2. Required dependencies installed")
        print("3. Network access for web search tools")


if __name__ == "__main__":
    asyncio.run(main()) 