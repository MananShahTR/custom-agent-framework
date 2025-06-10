#!/usr/bin/env python3
"""
Example script demonstrating the enhanced Deep Research Agent with source citations.

This script shows how the agent now automatically includes footnotes and source citations
in its responses, making it easy to trace information back to original sources.
"""

import asyncio
import os
from src.agents.deep_research import DeepResearchAgent, DeepResearchConfig

async def main():
    """Demonstrate the enhanced deep research agent with citations."""
    
    # Initialize the agent
    config = DeepResearchConfig(
        enable_sources=["web", "google_drive"],
        max_sources_per_query=5,
        verbose=True
    )
    
    agent = DeepResearchAgent(
        name="CitationResearchAgent",
        config=config,
        verbose=True
    )
    
    # Example research query
    query = "What are the latest developments in AI safety research in 2024?"
    
    print("🔍 Starting research with automatic source citations...")
    print(f"Query: {query}")
    print("-" * 60)
    
    # Conduct research and get detailed report
    report = await agent.conduct_research(query)
    
    print("\n" + "="*60)
    print("📋 RESEARCH RESULTS WITH CITATIONS")
    print("="*60)
    
    # The synthesis will now automatically include footnote citations [1], [2], etc.
    print(report.synthesis)
    
    print("\n" + "="*60)
    print("📚 ACCESSIBLE SOURCES")
    print("="*60)
    
    # Show clickable sources for easy access
    clickable_sources = report.clickable_sources
    if clickable_sources:
        print("Clickable sources for deeper investigation:")
        for citation_num, url in clickable_sources.items():
            source_title = report.get_source_by_citation(citation_num)
            print(f"[{citation_num}] {source_title}")
            print(f"    🔗 {url}")
            print()
    else:
        print("No direct clickable sources available.")
    
    # Show research summary
    summary = agent.get_research_summary()
    print(f"\n📊 Research Summary:")
    print(f"• Sources consulted: {summary['findings_count']}")
    print(f"• Source types: {', '.join(summary['source_types'])}")
    print(f"• Clickable citations: {summary['citations_available']}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main()) 