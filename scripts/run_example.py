#!/usr/bin/env python3
"""
Example Launcher - Properly sets up paths and runs multi-agent examples
"""

import sys
import os
import asyncio

# Change to project root to make module imports work
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Now we can import using module syntax
from src.agents.agent import Agent
from src.tools.handoff import HandoffTool


async def basic_handoff_demo():
    """Basic handoff demonstration."""
    
    print("🚀 Basic Handoff Demo")
    print("="*50)
    
    # Create two specialized agents
    researcher = Agent(
        name="Research Agent",
        description="I find and gather information",
        enable_web_search=True,
        verbose=True
    )
    
    writer = Agent(
        name="Writing Agent", 
        description="I create clear, engaging content",
        verbose=True
    )
    
    # Add handoff capability
    researcher.tools.append(HandoffTool(writer))
    writer.tools.append(HandoffTool(researcher))
    
    # Set agent names for beautiful logging
    for tool in researcher.tools:
        if isinstance(tool, HandoffTool):
            tool.set_current_agent(researcher.name)
            
    for tool in writer.tools:
        if isinstance(tool, HandoffTool):
            tool.set_current_agent(writer.name)
    
    print("🎯 Demo: Research → Writing handoff")
    
    # Start with researcher - it should research then handoff to writer
    result = await researcher.run_async(
        "Research recent developments in AI safety, then create a brief summary document"
    )
    
    print("\n✅ Task completed with beautiful agent handoffs!")


async def multi_agent_demo():
    """Multi-agent coordination demonstration."""
    
    print("\n🚀 Multi-Agent System Demo")
    print("="*80)
    
    # Create specialized agents
    research_agent = Agent(
        name="Research Specialist",
        description="Deep research and analysis", 
        enable_web_search=True,
        verbose=True
    )

    writing_agent = Agent(
        name="Writing Specialist",
        description="Content creation and editing",
        verbose=True
    )

    analysis_agent = Agent(
        name="Analysis Specialist", 
        description="Data analysis and insights",
        verbose=True
    )

    # Set up handoff connections
    research_agent.tools.extend([
        HandoffTool(writing_agent),
        HandoffTool(analysis_agent)
    ])

    writing_agent.tools.append(HandoffTool(research_agent))
    analysis_agent.tools.append(HandoffTool(writing_agent))

    # Create orchestrator
    orchestrator = Agent(
        name="Orchestrator",
        description="Coordinates complex tasks",
        tools=[
            HandoffTool(research_agent),
            HandoffTool(writing_agent), 
            HandoffTool(analysis_agent)
        ],
        enable_web_search=True,
        verbose=True,
        system_prompt="""You are an Orchestrator that coordinates tasks between specialist agents.

Available specialists:
- Research Specialist: Use for research and information gathering
- Writing Specialist: Use for content creation and editing  
- Analysis Specialist: Use for data analysis and insights

For complex tasks, delegate to the most appropriate specialist."""
    )

    # Set current agent names for beautiful logging
    for agent in [research_agent, writing_agent, analysis_agent, orchestrator]:
        for tool in agent.tools:
            if isinstance(tool, HandoffTool):
                tool.set_current_agent(agent.name)

    print("✅ Multi-agent system ready!")
    
    # Demo task
    print("\n🎯 DEMO: Complex Research and Analysis Task")
    print("="*80)
    
    result = await orchestrator.run_async(
        "Research the latest developments in quantum computing, analyze the key trends, and write a comprehensive summary"
    )
    
    print("\n🎉 Multi-agent demo completed!")


async def main():
    """Run both demos."""
    
    print("🌟 Multi-Agent System Demonstrations")
    print("="*100)
    
    # Run basic demo
    await basic_handoff_demo()
    
    # Run advanced demo
    await multi_agent_demo()
    
    print("\n✨ All demos completed successfully!")


if __name__ == "__main__":
    asyncio.run(main()) 