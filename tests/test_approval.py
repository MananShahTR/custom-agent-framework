"""Test script for human-in-the-loop approval system."""

import asyncio
import sys
import os

# Add parent directory to Python path to import src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.agents import Agent
from src.tools import GoogleDriveTool, GoogleDriveContentTool, RequestApprovalTool


async def test_approval_system():
    """Test the approval system with Google Drive tools."""
    print("🤖 Testing Human-in-the-Loop Approval System")
    print("=" * 60)
    
    # Create an agent with Google Drive tools and approval
    agent = Agent(
        name="TestAgent",
        description="An agent for testing human-in-the-loop approval with Google Drive",
        tools=[
            GoogleDriveTool(),
            GoogleDriveContentTool(),
            RequestApprovalTool()
        ],
        verbose=True
    )
    
    print("\n📋 Testing Google Drive search with approval...")
    print("This should prompt for approval before searching Google Drive.")
    
    # Test direct tool usage (will require approval)
    try:
        drive_tool = GoogleDriveTool()
        result = await drive_tool.execute(query="test documents", max_results=3)
        print(f"\n📄 Search Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🤖 Testing agent with approval tool...")
    print("Try asking: 'Search my Google Drive for documents about project planning'")
    print("The agent should request approval before accessing Google Drive.")
    
    # Test agent usage
    user_input = "Search my Google Drive for documents about project planning"
    response = await agent.run_async(user_input)
    
    # Print response
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(f"\n🤖 Agent Response:\n{content.text}")


async def test_approval_decorator():
    """Test the approval decorator directly."""
    print("\n🧪 Testing approval decorator directly...")
    
    from src.utils.approval import require_approval
    
    @require_approval("This is a test operation that requires approval")
    async def test_operation():
        print("🎉 Test operation executed successfully!")
        return "Operation completed"
    
    result = await test_operation()
    print(f"Result: {result}")


async def main():
    """Main test function."""
    print("🚀 Human-in-the-Loop Approval System Test")
    print("=" * 60)
    
    # Test 1: Direct decorator test
    await test_approval_decorator()
    
    print("\n" + "=" * 60)
    
    # Test 2: Google Drive tools with approval
    await test_approval_system()


if __name__ == "__main__":
    asyncio.run(main()) 