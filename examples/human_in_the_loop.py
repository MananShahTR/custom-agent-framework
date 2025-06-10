"""Example of using human-in-the-loop approval system."""

import asyncio
import sys
import os

# Add parent directory to Python path to import src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storm_agentagents import Agent
from storm_agenttools import GoogleDriveTool, GoogleDriveContentTool, RequestApprovalTool, BraveSearchTool


async def basic_approval_example():
    """Example 1: Basic approval decorator usage."""
    print("📝 Example 1: Basic Approval Decorator")
    print("=" * 50)
    
    from storm_agentutils.approval import require_approval
    
    @require_approval("Perform a simulated expensive operation")
    async def expensive_operation():
        print("💰 Performing expensive operation...")
        await asyncio.sleep(1)  # Simulate work
        return "Operation completed successfully!"
    
    print("This will ask for approval before running:")
    result = await expensive_operation()
    print(f"Result: {result}")


async def google_drive_approval_example():
    """Example 2: Google Drive tools with approval."""
    print("\n📁 Example 2: Google Drive with Approval")
    print("=" * 50)
    
    # Create agent with Google Drive tools (they have approval built-in)
    agent = Agent(
        name="DriveAssistant",
        description="Assistant that can search and read Google Drive files with user approval",
        tools=[
            GoogleDriveTool(),
            GoogleDriveContentTool(),
            RequestApprovalTool()
        ],
        verbose=True
    )
    
    print("Agent created with Google Drive tools that require approval.")
    print("Try asking: 'Search my Google Drive for budget documents'")
    print("The tool will ask for approval before accessing your Drive.\n")
    
    # Interactive session
    user_input = input("Enter your request (or press Enter for default): ").strip()
    if not user_input:
        user_input = "Search my Google Drive for budget documents"
    
    response = await agent.run_async(user_input)
    
    # Print response
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(f"\n🤖 Response:\n{content.text}")


async def agent_initiated_approval_example():
    """Example 3: Agent-initiated approval."""
    print("\n🤖 Example 3: Agent-Initiated Approval")
    print("=" * 50)
    
    # Create agent with approval tool and web search
    agent = Agent(
        name="CautiousAgent",
        description="A cautious agent that asks for approval before expensive operations",
        tools=[
            BraveSearchTool(),
            RequestApprovalTool()
        ],
        verbose=True
    )
    
    print("This agent has been instructed to request approval for potentially expensive operations.")
    print("Try asking: 'Research the latest developments in AI and write a comprehensive report'")
    print("The agent should request approval before starting extensive research.\n")
    
    user_input = input("Enter your request (or press Enter for default): ").strip()
    if not user_input:
        user_input = "Research the latest developments in AI and write a comprehensive report"
    
    response = await agent.run_async(user_input)
    
    # Print response
    if hasattr(response, 'content'):
        for content in response.content:
            if hasattr(content, 'text'):
                print(f"\n🤖 Response:\n{content.text}")


async def main():
    """Run all examples."""
    print("🚀 Human-in-the-Loop Approval Examples")
    print("=" * 60)
    
    try:
        # Example 1: Basic decorator
        await basic_approval_example()
        
        # Example 2: Google Drive with approval
        await google_drive_approval_example()
        
        # Example 3: Agent-initiated approval
        await agent_initiated_approval_example()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 