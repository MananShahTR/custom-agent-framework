"""Example of using the DeepResearchAgent with web sources only (no Google Drive needed)."""

import asyncio
import sys
import os

# Add parent directory to Python path to import src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storm_agentagents import DeepResearchAgent, DeepResearchConfig


async def web_only_research_example():
    """Example using web sources only (no Google Drive credentials required)."""
    print("🔬 Web-Only Deep Research Example")
    print("=" * 60)
    
    # Create configuration for web-only research
    config = DeepResearchConfig(
        enable_sources=["web"],  # Only web sources
        enable_google_drive=False,  # Explicitly disable Google Drive
        verbose=True,
        max_tokens=2048
    )
    
    # Initialize the research agent
    agent = DeepResearchAgent(
        name="WebResearcher",
        config=config,
        verbose=True
    )
    
    # Simple research query
    query = "What are the latest trends in artificial intelligence for 2024?"
    
    print(f"\n🔍 Research Query: {query}")
    print("-" * 60)
    
    try:
        # Conduct research
        response = await agent.run_async(query)
        
        # Display the response
        if hasattr(response, 'content'):
            for content in response.content:
                if hasattr(content, 'text'):
                    print(f"\n📖 Research Results:\n{content.text}")
    
    except Exception as e:
        print(f"❌ Error during research: {e}")


async def main():
    """Main function."""
    print("🚀 Deep Research Agent - Web Only Example")
    print("This example works without Google Drive credentials")
    print("=" * 70)
    
    await web_only_research_example()


if __name__ == "__main__":
    asyncio.run(main()) 