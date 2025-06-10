#!/usr/bin/env python3
"""
Interactive conversational MCP server integration example for Storm Agent.

This example demonstrates:
1. Real-time interactive conversations with MCP tools
2. Multiple MCP server configurations
3. How tools persist across conversation turns
4. Real-world scenarios with user input

To run this example, you'll need:
1. pip install storm-agent
2. MCP servers configured (filesystem, custom SSE, etc.)
"""

import asyncio
import sys
import os

from storm_agent import Agent


async def interactive_conversation():
    """Interactive conversation with MCP tools."""
    
    # Configure MCP servers (restored original configuration)
    mcp_servers = [
        {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/mananshah/Documents/git/anthropic-tests"],
            "env": {}
        },
        {
            "type": "sse", 
            "url": "https://my-mcp-server.mananshah1403.workers.dev/sse"
        }
    ]
    
    # Create agent with MCP servers
    agent = Agent(
        name="Interactive Assistant",
        description="A helpful assistant that can use MCP tools interactively",
        mcp_servers=mcp_servers,
        verbose=True
    )
    
    try:
        print("🚀 Starting Interactive MCP Conversation...")
        print("=" * 60)
        print("💡 Tips:")
        print("  - Type 'help' for MCP tool information")
        print("  - Type 'quit' or 'exit' to end the conversation")
        print("  - Type 'clear' to clear the screen")
        print("  - Just chat naturally - the agent will use MCP tools as needed!")
        print("=" * 60)
        
        turn_count = 0
        
        while True:
            turn_count += 1
            print(f"\n--- Turn {turn_count} ---")
            
            # Get user input
            try:
                user_input = input("👤 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Conversation ended by user")
                break
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            elif user_input.lower() == 'help':
                print_help_info()
                continue
            elif not user_input:
                print("Please enter a message or 'quit' to exit.")
                continue
            
            # Get agent response
            print("\n🤖 Assistant:")
            try:
                response = await agent.run_async(user_input)
                
                # Display response
                for content in response.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                        
            except Exception as e:
                print(f"❌ Error getting response: {e}")
        
    except Exception as e:
        print(f"\n❌ Error in conversation: {e}")
    finally:
        # Clean up MCP connections
        await agent.cleanup()
        print("\n🧹 MCP connections cleaned up")


def print_help_info():
    """Print help information about MCP tools and usage."""
    print("\n📚 MCP Tools Help:")
    print("-" * 40)
    print("Your agent has access to multiple MCP servers:")
    print("\n🗂️  FILESYSTEM SERVER:")
    print("  - Read, write, edit files")
    print("  - List directories, create folders") 
    print("  - Move, search, get file info")
    print("  - Directory: /Users/mananshah/Documents/git/anthropic-tests")
    
    print("\n🌐 CUSTOM SSE SERVER:")
    print("  - Your custom MCP server at mananshah1403.workers.dev")
    print("  - Tools depend on your server implementation")
    
    print("\n💡 Example requests:")
    print("  - 'List files in the current directory'")
    print("  - 'Create a new file called test.md with some content'")
    print("  - 'Help me organize my project files'")
    print("  - 'What tools do you have available from the custom server?'")
    print("  - 'Search for Python files in the project'")


async def quick_demo():
    """Quick single-turn demo."""
    
    mcp_servers = [
        {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/mananshah/Documents/git/anthropic-tests"],
            "env": {}
        },
        {
            "type": "sse", 
            "url": "https://my-mcp-server.mananshah1403.workers.dev/sse"
        }
    ]
    
    agent = Agent(
        name="Quick Demo Agent",
        description="A quick demo agent",
        mcp_servers=mcp_servers,
        verbose=False
    )
    
    try:
        print("\n🔄 Quick Demo - Listing available tools...")
        response = await agent.run_async(
            "What MCP tools do you have available? Please list them with brief descriptions."
        )
        
        print("🤖 Available Tools:")
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
                
    finally:
        await agent.cleanup()


def show_conversation_examples():
    """Show example conversation patterns."""
    
    examples = {
        "File Operations": [
            "Show me what files are in this project",
            "Create a new Python file for my script",
            "Read the contents of README.md",
            "Move all .txt files to a docs folder"
        ],
        
        "Project Management": [
            "Help me organize my project structure", 
            "Create a new folder for my experiments",
            "Find all Python files that mention 'agent'",
            "Generate a project summary based on files"
        ],
        
        "Custom Server Tasks": [
            "What can you do with the custom MCP server?",
            "Use the custom server to [specific task]",
            "Show me data from the SSE server",
            "Process this request through the custom endpoint"
        ]
    }
    
    print("💡 Example Conversation Starters:")
    for category, prompts in examples.items():
        print(f"\n{category.upper()}:")
        for prompt in prompts:
            print(f"  💬 '{prompt}'")


if __name__ == "__main__":
    print("🌩️ Storm Agent - Interactive MCP Conversation Demo")
    print("=" * 50)
    
    show_conversation_examples()
    
    print(f"\n{'='*50}")
    print("🎮 Choose mode:")
    print("1. Interactive conversation (recommended)")
    print("2. Quick demo (see available tools)")
    print("3. Help info only")
    
    try:
        choice = input("\nEnter choice (1-3) or press Enter for interactive: ").strip()
        if not choice:
            choice = "1"
            
        if choice == "1":
            print(f"\n{'='*50}")
            print("🗣️  INTERACTIVE MODE")
            print("="*50)
            asyncio.run(interactive_conversation())
            
        elif choice == "2":
            asyncio.run(quick_demo())
            
        elif choice == "3":
            print_help_info()
            
        else:
            print("Invalid choice, starting interactive mode...")
            asyncio.run(interactive_conversation())
            
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your MCP server configurations and try again.")
