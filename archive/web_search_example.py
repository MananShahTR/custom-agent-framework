"""Example usage of the Enhanced WebSearchAgent with Brave Search and Firecrawl."""

import os
from dotenv import load_dotenv
from web_search_agent import WebSearchAgent, ModelConfig

# Load environment variables from .env file
load_dotenv()

def main():
    """Demonstrate various uses of the Enhanced WebSearchAgent."""
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set your ANTHROPIC_API_KEY environment variable")
        return
    
    print("🔍 Enhanced WebSearchAgent Example")
    print("=" * 60)
    
    # Initialize the agent with verbose output
    agent = WebSearchAgent(
        name="EnhancedResearchAssistant",
        verbose=True,
        config=ModelConfig(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,  # Increased for longer responses
            temperature=0.2   # Lower temperature for more focused responses
        )
    )
    
    # Example 1: Current AI developments with detailed extraction
    print("\n🤖 Example 1: Current AI Research")
    print("-" * 40)
    try:
        response = agent.run("Find the latest breakthroughs in large language models and AI reasoning from 2024. Please extract detailed content from at least one recent research paper or article.")
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Climate research with multiple source verification
    print("\n🌍 Example 2: Climate Research Analysis")
    print("-" * 40)
    try:
        response = agent.run("Research the latest findings about ocean temperature changes and their impact on marine ecosystems. Please find recent scientific publications and extract key findings.")
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Direct tool usage demonstrations
    print("\n🔧 Example 3: Direct Tool Usage")
    print("-" * 40)
    try:
        # Direct Brave search
        print("📍 Direct Brave Search:")
        search_result = agent.search_web("Anthropic Claude 4 features capabilities", count=3)
        print(f"{search_result}\n")
        
        # Direct Firecrawl extraction
        print("📍 Direct Content Extraction:")
        # Using a sample URL (replace with actual URL from search results)
        content = agent.extract_content("https://www.anthropic.com", max_length=1000)
        print(f"{content}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Interactive session
    print("\n💬 Example 4: Interactive Research Session")
    print("-" * 40)
    interactive_demo(agent)

def print_response(response):
    """Helper function to print Claude's response."""
    text_content = ""
    for block in response.content:
        if block.type == "text":
            text_content += block.text
    print(f"🤖 Response:\n{text_content}\n")

def interactive_demo(agent):
    """Run an interactive demo with the enhanced agent."""
    print("Enter your research questions (type 'quit' to exit):")
    print("💡 Try questions like:")
    print("   - 'Find recent papers on quantum computing advances'")
    print("   - 'Research cybersecurity threats in cloud computing'")
    print("   - 'What are the latest developments in renewable energy storage?'")
    
    while True:
        try:
            user_input = input("\n❓ Your research question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Processing research request...")
            response = agent.run(user_input)
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def advanced_research_example():
    """Example of conducting advanced research with multiple search strategies."""
    
    # Custom system prompt for specialized research
    research_prompt = """You are a specialized research assistant with access to advanced web search and content extraction tools.

**Research Strategy:**
1. **Comprehensive Search**: Use multiple targeted searches to gather information from different angles
2. **Source Verification**: Cross-reference information from multiple authoritative sources
3. **Deep Content Analysis**: Extract full content from the most relevant articles for detailed analysis
4. **Critical Evaluation**: Assess the credibility and recency of sources
5. **Synthesis**: Combine findings into coherent, well-sourced conclusions

**Content Extraction Guidelines:**
- Prioritize recent academic papers, official reports, and authoritative news sources
- Extract methodology, key findings, and conclusions from research papers
- Note publication dates and author credentials
- Identify any limitations or conflicting viewpoints

**Response Structure:**
1. **Executive Summary**: Brief overview of key findings
2. **Detailed Analysis**: In-depth discussion with source citations
3. **Source Evaluation**: Assessment of source quality and recency
4. **Implications**: What these findings mean for the field
5. **Further Research**: Suggested areas for additional investigation

Always maintain academic rigor and provide complete source attribution."""
    
    # Create a specialized research agent
    research_agent = WebSearchAgent(
        name="AdvancedResearcher",
        system=research_prompt,
        verbose=True,
        config=ModelConfig(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.1  # Very focused for research
        )
    )
    
    # Complex research query
    query = """Conduct a comprehensive research analysis on the current state of autonomous vehicle safety systems. 
    Please search for recent studies, regulatory updates, and industry reports. Extract detailed content from at least 
    2-3 authoritative sources and provide a thorough analysis of the technology's current capabilities, limitations, 
    and future prospects."""
    
    print("\n🔬 Advanced Research Agent Example")
    print("=" * 50)
    print(f"Research Query: {query}")
    print("-" * 50)
    
    try:
        response = research_agent.run(query)
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")

def api_status_check():
    """Check the status of all required API keys."""
    print("\n🔑 API Configuration Check")
    print("=" * 40)
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    
    print(f"Anthropic API: {'✅ Configured' if anthropic_key else '❌ Missing'}")
    print(f"Brave Search API: {'✅ Configured' if brave_key else '⚠️  Missing (fallback available)'}")
    print(f"Firecrawl API: {'✅ Configured' if firecrawl_key else '⚠️  Missing (fallback available)'}")
    
    if not anthropic_key:
        print("\n❌ Anthropic API key is required for the agent to function.")
        print("   Add ANTHROPIC_API_KEY to your .env file")
    
    if not brave_key:
        print("\n⚠️  For optimal search results, add BRAVE_SEARCH_API_KEY to your .env file")
        print("   Get your key at: https://api.search.brave.com/")
    
    if not firecrawl_key:
        print("\n⚠️  For enhanced content extraction, add FIRECRAWL_API_KEY to your .env file")
        print("   Get your key at: https://www.firecrawl.dev/")

if __name__ == "__main__":
    # Check API configuration first
    api_status_check()
    
    # Run main examples
    main()
    
    # Run advanced research example
    advanced_research_example() 