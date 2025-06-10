"""Example usage of the DeepResearchAgent with ReAct framework."""

import asyncio
from deep_research_agent import DeepResearchAgent, DeepResearchConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_basic_research():
    """Basic example of using the DeepResearchAgent."""
    print("🚀 Basic Research Example")
    print("=" * 60)
    
    # Initialize with default configuration
    agent = DeepResearchAgent()
    
    # Run a simple research query
    query = "What are the best practices for Python async programming?"
    report = agent.run(query)
    
    # Display results
    print(f"\n📄 Research Report")
    print(f"Query: {report.query}")
    print(f"Confidence: {report.confidence_level:.2%}")
    print(f"Sources: {', '.join(report.sources_consulted.keys())}")
    print(f"\n📝 Summary:\n{report.synthesis}")


def example_custom_config():
    """Example with custom configuration."""
    print("\n🔧 Custom Configuration Example")
    print("=" * 60)
    
    # Create custom configuration
    config = DeepResearchConfig(
        enable_sources=["web"],  # Only use web search
        research_depth="shallow",  # Quick research
        verbose=False  # Less output
    )
    
    agent = DeepResearchAgent(config=config)
    
    query = "Latest news about artificial intelligence"
    report = agent.run(query)
    
    print(f"Completed in {report.iterations_performed} iterations")
    print(f"Confidence: {report.confidence_level:.2%}")


def example_multi_source():
    """Example using multiple data sources."""
    print("\n🌐 Multi-Source Research Example")
    print("=" * 60)
    
    # Configure for multiple sources
    config = DeepResearchConfig(
        enable_sources=["web", "google_drive"],
        research_depth="deep",
        verbose=True
    )
    
    agent = DeepResearchAgent(config=config)
    
    # This query might search both web and Google Drive
    query = "Company quarterly performance metrics and industry comparison"
    
    try:
        report = agent.run(query)
        
        # Show which sources were actually used
        print(f"\n📊 Research Statistics:")
        for source, queries in report.sources_consulted.items():
            print(f"  - {source}: {len(queries)} queries")
            for q in queries[:2]:  # Show first 2 queries
                print(f"    • {q}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Note: Google Drive requires authentication setup")


async def example_async_research():
    """Example of async research for multiple queries."""
    print("\n⚡ Async Research Example")
    print("=" * 60)
    
    agent = DeepResearchAgent(
        config=DeepResearchConfig(verbose=False)
    )
    
    queries = [
        "What is quantum computing?",
        "How does machine learning work?",
        "What are the latest developments in robotics?"
    ]
    
    # Run multiple researches concurrently
    async def research_task(query):
        report = await agent.conduct_research(query)
        return query, report.confidence_level, len(report.findings)
    
    # Execute all queries concurrently
    results = await asyncio.gather(*[research_task(q) for q in queries])
    
    # Display results
    print("Concurrent research results:")
    for query, confidence, findings_count in results:
        print(f"  • {query}")
        print(f"    Confidence: {confidence:.2%}, Findings: {findings_count}")


def example_research_analysis():
    """Example showing detailed analysis of research findings."""
    print("\n🔍 Detailed Research Analysis Example")
    print("=" * 60)
    
    config = DeepResearchConfig(
        enable_sources=["web"],
        verbose=False
    )
    
    agent = DeepResearchAgent(config=config)
    
    query = "What are the environmental impacts of electric vehicles?"
    report = agent.run(query)
    
    # Analyze findings by source
    print(f"Research Query: {query}")
    print(f"Total Findings: {len(report.findings)}")
    print(f"\nFindings Breakdown:")
    
    # Group findings by source type
    by_source = {}
    for finding in report.findings:
        source = finding.source_type.value
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(finding)
    
    for source, findings in by_source.items():
        print(f"\n📌 From {source} ({len(findings)} findings):")
        for i, finding in enumerate(findings[:3], 1):  # Show first 3
            print(f"  {i}. {finding.source_title or 'Untitled'}")
            print(f"     Relevance: {finding.relevance_score:.2f}")
            if finding.source_url:
                print(f"     URL: {finding.source_url}")


def main():
    """Run all examples."""
    print("🎯 DeepResearchAgent Examples")
    print("=" * 80)
    
    # Run basic example
    example_basic_research()
    
    # Run custom config example
    example_custom_config()
    
    # Run multi-source example (may fail without Google Drive auth)
    example_multi_source()
    
    # Run async example
    print("\nRunning async example...")
    asyncio.run(example_async_research())
    
    # Run analysis example
    example_research_analysis()
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    main() 