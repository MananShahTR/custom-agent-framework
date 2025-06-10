"""Example of using the Storm Agent DeepResearchAgent for comprehensive research."""

import asyncio
import sys

from storm_agent import DeepResearchAgent, DeepResearchConfig


async def main():
    """Run a conversational research assistant."""
    print("🔬 Deep Research Agent - Conversational Mode")
    print("=" * 60)
    
    # Create custom configuration
    config = DeepResearchConfig(
        enable_sources=["web", "google_drive"],
        enable_google_drive=True,
        verbose=True,
        max_tokens=4096
    )
    
    print("Initializing Deep Research Agent...")
    print("Note: This will attempt to use both web and Google Drive sources.")
    print("If Google Drive credentials are not available, it will fall back to web-only research.\n")
    
    # Initialize the research agent
    agent = DeepResearchAgent(
        name="ResearchAssistant",
        config=config,
        verbose=True
    )
    
    print("🤖 Research Assistant is ready! Type your questions or 'exit' to quit.")
    print("💡 Tip: Ask complex research questions for best results!")
    print("=" * 80)
    
    # Conversational loop
    while True:
        try:
            # Get user input
            print("\n" + "🔍 " + "="*76)
            user_query = input("You: ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n👋 Thanks for using the Research Assistant! Goodbye!")
                break
            
            # Skip empty queries
            if not user_query:
                print("❓ Please enter a research question or 'exit' to quit.")
                continue
            
            print("\n🔬 Researching your question...")
            print("=" * 80)
            
            # Conduct research and get a structured report
            report = await agent.conduct_research(user_query)
            
            # Display the research report
            print("\n" + "📊 RESEARCH REPORT")
            print("=" * 80)
            
            print(f"🗓️ **Generated:** {report.timestamp}")
            print(f"❓ **Query:** {report.query.strip()}")
            print(f"📚 **Findings:** {len(report.findings)} sources consulted")
            
            if report.sources_consulted:
                print("\n📋 **Sources Consulted:**")
                for source_type, queries in report.sources_consulted.items():
                    if queries:
                        print(f"  • {source_type.title()}: {len(queries)} searches")
                        for query in queries[:2]:  # Show first 2 queries to keep it concise
                            print(f"    - {query}")
                        if len(queries) > 2:
                            print(f"    - ... and {len(queries) - 2} more")
            
            print("\n" + "🔍 RESEARCH SYNTHESIS:")
            print("=" * 80)
            print(report.synthesis)
            
            # Show research summary
            summary = agent.get_research_summary()
            print(f"\n📈 **Session Stats:** {summary['findings_count']} findings | "
                  f"{summary['message_history']['message_count']} messages | "
                  f"{summary['message_history']['total_tokens']} tokens")
            
        except KeyboardInterrupt:
            print("\n\n👋 Research session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Research failed: {e}")
            print("💡 Try rephrasing your question or ask something else.")
            print("Tip: If this is a Google Drive authentication error,")
            print("try running the web-only example: python examples/deep_research_web_only.py")


async def quick_research_example():
    """Quick research example with web sources only."""
    # Simple configuration for web-only research
    config = DeepResearchConfig(
        enable_sources=["web"],
        enable_google_drive=False,
        verbose=True
    )
    
    agent = DeepResearchAgent(config=config)
    
    query = "What are the main benefits and risks of remote work based on recent studies?"
    
    print(f"\n🔍 Quick research: {query}")
    print("-" * 60)
    
    # Use the regular run method instead of conduct_research
    response = await agent.run_async(query)
    
    # Print response
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)


async def demo_mode():
    """Run a single demo query for testing."""
    print("🔬 Deep Research Agent - Demo Mode")
    print("=" * 60)
    
    # Create custom configuration
    config = DeepResearchConfig(
        enable_sources=["web", "google_drive"],
        enable_google_drive=True,
        verbose=True,
        max_tokens=4096
    )
    
    print("Initializing Deep Research Agent...")
    
    # Initialize the research agent
    agent = DeepResearchAgent(
        name="ResearchAssistant",
        config=config,
        verbose=True
    )
    
    # Demo research query
    query = """
    Find me the cheapest flight to Mumbai based on where my passport was issued. My name is Manan
    """
    
    print(f"🔬 Demo research query: {query.strip()}")
    print("=" * 80)
    
    try:
        # Conduct research and get a structured report
        report = await agent.conduct_research(query)
        
        # Display the research report
        print("\n" + "=" * 80)
        print("📊 RESEARCH REPORT")
        print("=" * 80)
        
        print(f"🗓️ **Generated:** {report.timestamp}")
        print(f"❓ **Query:** {report.query.strip()}")
        print(f"📚 **Findings:** {len(report.findings)} sources consulted")
        
        print("\n📋 **Sources Consulted:**")
        for source_type, queries in report.sources_consulted.items():
            if queries:
                print(f"  • {source_type.title()}: {len(queries)} searches")
                for query in queries[:3]:  # Show first 3 queries
                    print(f"    - {query}")
                if len(queries) > 3:
                    print(f"    - ... and {len(queries) - 3} more")
        
        print("\n" + "=" * 80)
        print("🔍 **RESEARCH SYNTHESIS:**")
        print("=" * 80)
        print(report.synthesis)
        
        print("\n" + "=" * 80)
        print("📈 **RESEARCH SUMMARY:**")
        print("=" * 80)
        summary = agent.get_research_summary()
        print(f"• Total findings: {summary['findings_count']}")
        print(f"• Source types used: {', '.join(summary['source_types'])}")
        print(f"• Message history: {summary['message_history']['message_count']} messages")
        print(f"• Total tokens used: {summary['message_history']['total_tokens']}")
        
    except Exception as e:
        print(f"\n❌ Research failed: {e}")
        print("\nTip: If this is a Google Drive authentication error,")
        print("try running the web-only example: python examples/deep_research_web_only.py")


if __name__ == "__main__":
    print("🌩️ Storm Agent - Deep Research Example")
    print("=" * 80)
    
    # Check for demo mode argument
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_mode())
    else:
        # Run conversational mode by default
        asyncio.run(main())
    
    # # Run quick research example
    # asyncio.run(quick_research_example())
