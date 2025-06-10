"""Test script to show actual extracted content from Google Drive PDFs."""

import asyncio
import sys
import os

# Add parent directory to Python path to import src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.agents import DeepResearchAgent, DeepResearchConfig


async def test_pdf_extraction():
    """Test PDF extraction to see actual content."""
    print("🔍 Testing PDF Content Extraction")
    print("=" * 60)
    
    # Create configuration for Google Drive only
    config = DeepResearchConfig(
        enable_sources=["google_drive"],
        enable_google_drive=True,
        verbose=True,
        max_tokens=2048
    )
    
    # Initialize the research agent
    agent = DeepResearchAgent(
        name="ExtractorAgent",
        config=config,
        verbose=True
    )
    
    # Search for passport documents and extract content
    query = "Find passport documents in my google drive and show me the extracted text content"
    
    print(f"\n🔍 Query: {query}")
    print("-" * 60)
    
    try:
        # Run the extraction
        response = await agent.run_async(query)
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")


if __name__ == "__main__":
    asyncio.run(test_pdf_extraction()) 