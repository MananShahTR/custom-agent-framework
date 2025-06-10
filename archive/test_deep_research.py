"""Simple test script for DeepResearchAgent."""

import os
from deep_research_agent import DeepResearchAgent, DeepResearchConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_basic_functionality():
    """Test basic agent functionality."""
    print("🧪 Testing DeepResearchAgent")
    print("=" * 60)
    
    # Check API keys
    print("📋 Checking API keys...")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("   Please add: ANTHROPIC_API_KEY=your_key_here")
        return
    else:
        print("✅ Anthropic API key found")
    
    # Test with web search only (doesn't require additional auth)
    print("\n🌐 Testing web search functionality...")
    
    try:
        config = DeepResearchConfig(
            enable_sources=["web"],
            research_depth="shallow",
            verbose=True
        )
        
        agent = DeepResearchAgent(config=config)
        
        # Simple test query
        query = "What is the capital of France?"
        print(f"\n🔍 Test query: {query}")
        
        report = agent.run(query)
        
        print(f"\n✅ Research completed successfully!")
        print(f"   Confidence: {report.confidence_level:.2%}")
        print(f"   Iterations: {report.iterations_performed}")
        print(f"   Findings: {len(report.findings)}")
        print(f"\n📝 Summary preview:")
        print(f"   {report.synthesis[:200]}...")
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()


def test_google_drive_auth():
    """Test Google Drive authentication."""
    print("\n\n🔐 Testing Google Drive authentication...")
    print("=" * 60)
    
    # Check for Google Drive auth methods
    auth_methods = []
    
    if os.path.exists('token.pickle'):
        auth_methods.append("OAuth2 token (token.pickle)")
    
    service_account = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    if service_account and os.path.exists(service_account):
        auth_methods.append(f"Service account ({service_account})")
    
    if not auth_methods:
        print("⚠️  No Google Drive authentication found")
        print("   To enable Google Drive search, set up one of:")
        print("   1. OAuth2 authentication (creates token.pickle)")
        print("   2. Service account (set GOOGLE_SERVICE_ACCOUNT_FILE in .env)")
    else:
        print("✅ Found authentication methods:")
        for method in auth_methods:
            print(f"   - {method}")
        
        # Try to initialize Google Drive tool
        try:
            from deep_research_agent import GoogleDriveTool
            tool = GoogleDriveTool()
            if tool.service:
                print("✅ Google Drive service initialized successfully")
            else:
                print("❌ Google Drive service initialization failed")
        except Exception as e:
            print(f"❌ Error testing Google Drive: {str(e)}")


if __name__ == "__main__":
    test_basic_functionality()
    test_google_drive_auth()
    
    print("\n\n🎉 Testing complete!")
    print("   Run 'python example_deep_research.py' for more examples") 