#!/usr/bin/env python3
"""
Basic Handoff Demo - Minimal Example

Shows the simplest possible multi-agent setup using existing Agent class + HandoffTool.
"""

import asyncio
import sys
import os

# Change to project root to make module imports work
project_root = os.path.join(os.path.dirname(__file__), '..')
project_root = os.path.abspath(project_root)
os.chdir(project_root)

# Add project root to Python path so it can find 'src' module
sys.path.insert(0, project_root)

# Now we can import using module syntax that works
from storm_agentagents.agent import Agent
from storm_agenttools.handoff import HandoffTool


async def main():
    """Basic handoff demonstration."""
    
    # Create two specialized agents using existing Agent class
    researcher = Agent(
        name="Research Agent",
        description="I find and gather information",
        verbose=True
    )
    
    writer = Agent(
        name="Writing Agent", 
        description="I create clear, engaging content",
        verbose=True
    )
    
    # Add handoff capability: researcher can handoff to writer
    researcher.tools.append(HandoffTool(writer))
    
    # Add handoff capability: writer can handoff back to researcher  
    writer.tools.append(HandoffTool(researcher))
    
    # Set agent names for beautiful logging
    for tool in researcher.tools:
        if isinstance(tool, HandoffTool):
            tool.set_current_agent(researcher.name)
            
    for tool in writer.tools:
        if isinstance(tool, HandoffTool):
            tool.set_current_agent(writer.name)
    
    print("🎯 Demo: Analysis → Writing handoff")
    print("="*50)
    
    # Start with researcher doing a simple analysis task
    result = await researcher.run_async(
        "Analyze the benefits of renewable energy and then create a brief summary document"
    )
    
    print("\n✅ Task completed with beautiful agent handoffs!")


if __name__ == "__main__":
    print("🚀 Basic Handoff Demo")
    asyncio.run(main()) 