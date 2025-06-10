"""Basic example of using the Storm Agent WebSearchAgent."""

import asyncio
from storm_agent import WebSearchAgent


async def main():
    """Run a basic web search example."""
    # Initialize the agent
    agent = WebSearchAgent(verbose=True)
    
    # Ask a question that requires web search
    query = "What are the latest developments in AI research in 2024?"
    
    print(f"🔍 Searching for: {query}")
    print("=" * 50)
    
    # Run the agent
    response = await agent.run_async(query)
    
    # Print the final response
    print("\n" + "=" * 50)
    print("📋 FINAL RESPONSE:")
    print("=" * 50)
    
    # Extract and print text content
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
    
    print("\n" + "=" * 50)
    print("✅ Search completed!")


def main_sync():
    """Synchronous version using the run() method."""
    # Initialize the agent
    agent = WebSearchAgent(verbose=True)
    
    # Ask a question
    query = "What is the current weather in San Francisco?"
    
    print(f"🔍 Searching for: {query}")
    print("=" * 50)
    
    # Run the agent synchronously
    response = agent.run(query)
    
    # Print the final response
    print("\n" + "=" * 50)
    print("📋 FINAL RESPONSE:")
    print("=" * 50)
    
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)


if __name__ == "__main__":
    print("🌩️ Storm Agent - Web Search Example")
    print("=" * 50)
    
    # You can run either async or sync version
    print("Running async version...")
    asyncio.run(main())
    
    print("\n" + "=" * 70)
    print("Running sync version...")
    main_sync()
