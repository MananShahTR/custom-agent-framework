"""Test script for the Enhanced WebSearchAgent with Brave Search and Firecrawl."""

import os
import asyncio
from dotenv import load_dotenv
from web_search_agent import WebSearchAgent, BraveSearchTool, FirecrawlContentTool

# Load environment variables from .env file
load_dotenv()

def test_api_keys():
    """Test API key configuration."""
    print("🔑 Testing API Key Configuration")
    print("=" * 50)
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    
    print(f"Anthropic API: {'✅ Found' if anthropic_key else '❌ Missing'}")
    print(f"Brave Search API: {'✅ Found' if brave_key else '⚠️  Missing (will use fallback)'}")
    print(f"Firecrawl API: {'✅ Found' if firecrawl_key else '⚠️  Missing (will use fallback)'}")
    
    return bool(anthropic_key)

def test_tools_standalone():
    """Test the individual tools without the full agent."""
    print("\n🧪 Testing Individual Tools")
    print("=" * 50)
    
    # Test BraveSearchTool
    print("\n1. Testing BraveSearchTool...")
    search_tool = BraveSearchTool()
    
    try:
        result = asyncio.run(search_tool.execute("Python programming language", count=3))
        print(f"✅ BraveSearchTool works!")
        print(f"Result preview: {result[:300]}...")
    except Exception as e:
        print(f"❌ BraveSearchTool error: {e}")
    
    # Test FirecrawlContentTool
    print("\n2. Testing FirecrawlContentTool...")
    content_tool = FirecrawlContentTool()
    
    try:
        # Test with a simple URL
        result = asyncio.run(content_tool.execute("https://httpbin.org/html", max_length=500))
        print(f"✅ FirecrawlContentTool works!")
        print(f"Result preview: {result[:300]}...")
    except Exception as e:
        print(f"❌ FirecrawlContentTool error: {e}")

def test_agent_initialization():
    """Test agent initialization without making API calls."""
    print("\n🤖 Testing Enhanced Agent Initialization")
    print("=" * 50)
    
    try:
        agent = WebSearchAgent(
            name="TestAgent",
            verbose=True
        )
        
        print(f"✅ Agent initialized successfully!")
        print(f"Agent name: {agent.name}")
        print(f"Number of tools: {len(agent.tools)}")
        print(f"Available tools: {[tool.name for tool in agent.tools]}")
        
        # Test tool dictionary creation
        tool_dict = {tool.name: tool for tool in agent.tools}
        print(f"Tool dictionary keys: {list(tool_dict.keys())}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return None

def test_with_real_api(agent):
    """Test with real API key if available."""
    print("\n🔑 Testing with Real Anthropic API")
    print("=" * 50)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  No Anthropic API key found. Skipping real API tests.")
        return
    
    try:
        # Simple test query
        print("Testing simple web search query...")
        response = agent.run("What is artificial intelligence?")
        
        # Extract text content
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text
        
        print(f"✅ Agent works with real API!")
        print(f"Response length: {len(text_content)} characters")
        print(f"Response preview: {text_content[:500]}...")
        
    except Exception as e:
        print(f"❌ Real API test error: {e}")

def test_tool_schemas():
    """Test that tool schemas are properly formatted."""
    print("\n📋 Testing Tool Schemas")
    print("=" * 50)
    
    tools = [BraveSearchTool(), FirecrawlContentTool()]
    
    for tool in tools:
        print(f"\nTool: {tool.name}")
        try:
            schema = tool.to_dict()
            
            # Check required fields
            required_fields = ["name", "description", "input_schema"]
            for field in required_fields:
                if field not in schema:
                    print(f"❌ Missing field: {field}")
                    continue
            
            print(f"✅ Schema valid for {tool.name}")
            print(f"   Description: {schema['description'][:80]}...")
            
            # Check input schema structure
            input_schema = schema["input_schema"]
            if "properties" in input_schema and "required" in input_schema:
                print(f"   Required params: {input_schema['required']}")
            
        except Exception as e:
            print(f"❌ Schema error for {tool.name}: {e}")

def test_direct_tool_usage():
    """Test direct tool usage methods."""
    print("\n🔧 Testing Direct Tool Usage")
    print("=" * 50)
    
    try:
        agent = WebSearchAgent(verbose=False)  # Quiet for testing
        
        # Test direct search
        print("1. Testing direct web search...")
        search_result = agent.search_web("OpenAI GPT", count=2)
        print(f"✅ Direct search successful!")
        print(f"Result length: {len(search_result)} characters")
        
        # Test direct content extraction (using a simple test URL)
        print("\n2. Testing direct content extraction...")
        content = agent.extract_content("https://httpbin.org/html", max_length=300)
        print(f"✅ Direct extraction successful!")
        print(f"Content length: {len(content)} characters")
        
    except Exception as e:
        print(f"❌ Direct tool usage error: {e}")

def test_search_parameters():
    """Test various search parameters."""
    print("\n🔍 Testing Search Parameters")
    print("=" * 50)
    
    search_tool = BraveSearchTool()
    
    test_cases = [
        {"query": "machine learning", "count": 3, "country": "US"},
        {"query": "climate change", "count": 2, "offset": 0},
        {"query": "quantum computing", "count": 1}
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n{i}. Testing with params: {params}")
        try:
            result = asyncio.run(search_tool.execute(**params))
            print(f"✅ Search {i} successful!")
            print(f"Result preview: {result[:200]}...")
        except Exception as e:
            print(f"❌ Search {i} failed: {e}")

def test_content_extraction_parameters():
    """Test various content extraction parameters."""
    print("\n🔥 Testing Content Extraction Parameters")
    print("=" * 50)
    
    content_tool = FirecrawlContentTool()
    
    test_cases = [
        {
            "url": "https://httpbin.org/html",
            "max_length": 500,
            "formats": ["markdown"]
        },
        {
            "url": "https://httpbin.org/html",
            "max_length": 300,
            "include_tags": ["p", "h1", "h2"]
        }
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n{i}. Testing extraction with params: {params}")
        try:
            result = asyncio.run(content_tool.execute(**params))
            print(f"✅ Extraction {i} successful!")
            print(f"Result preview: {result[:200]}...")
        except Exception as e:
            print(f"❌ Extraction {i} failed: {e}")

def main():
    """Run all tests."""
    print("🔍 Enhanced Web Search Agent Test Suite")
    print("=" * 60)
    
    # Check API keys first
    has_anthropic_key = test_api_keys()
    
    # Run tests
    test_tool_schemas()
    test_tools_standalone()
    test_search_parameters()
    test_content_extraction_parameters()
    
    agent = test_agent_initialization()
    
    if agent:
        test_direct_tool_usage()
        
        if has_anthropic_key:
            test_with_real_api(agent)
        else:
            print("\n⚠️  Skipping real API tests - no Anthropic API key found")
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed!")
    print("\n💡 Tips for optimal performance:")
    print("   • Add BRAVE_SEARCH_API_KEY for high-quality search results")
    print("   • Add FIRECRAWL_API_KEY for enhanced content extraction")
    print("   • Ensure ANTHROPIC_API_KEY is set for full functionality")

if __name__ == "__main__":
    main() 