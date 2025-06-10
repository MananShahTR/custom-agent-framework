#!/usr/bin/env python3
"""
Simple Multi-Agent System Demo

This demonstrates how to create a multi-agent system using the existing Agent class
with the new HandoffTool for beautiful agent-to-agent coordination.
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
    """Demonstrate simple multi-agent coordination."""
    
    print("🌟 Creating Multi-Agent System using existing Agent class...")
    
    # 1. Create agents directly using your existing Agent class
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

    # 2. Create handoff tools and add them directly
    print("\n🔗 Setting up handoff connections...")
    
    # Research agent can handoff to writing and analysis
    research_agent.tools.extend([
        HandoffTool(writing_agent),
        HandoffTool(analysis_agent)
    ])

    # Writing agent can handoff to research
    writing_agent.tools.append(HandoffTool(research_agent))

    # Analysis agent can handoff to writing
    analysis_agent.tools.append(HandoffTool(writing_agent))

    # 3. Create orchestrator with all handoff tools
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

For complex tasks, delegate to the most appropriate specialist. You can also handle simple tasks yourself."""
    )

    # Set current agent names on handoff tools for beautiful logging
    for agent in [research_agent, writing_agent, analysis_agent, orchestrator]:
        for tool in agent.tools:
            if isinstance(tool, HandoffTool):
                tool.set_current_agent(agent.name)

    print("✅ Multi-agent system ready!")
    
    # 4. Demo different types of tasks
    print("\n" + "="*80)
    print("🎯 DEMO: Simple Task (No Handoff Needed)")
    print("="*80)
    
    result1 = await orchestrator.run_async(
        "What is 2+2?"
    )
    
    print("\n" + "="*80)
    print("🎯 DEMO: Analysis Task")  
    print("="*80)
    
    result2 = await orchestrator.run_async(
        "Analyze the pros and cons of remote work vs office work"
    )
    
    print("\n🎉 Multi-agent demo completed!")
    
    # Show system summary
    print("\n📊 System Summary:")
    print(f"- Orchestrator: {orchestrator.name}")
    print(f"- Specialists: {research_agent.name}, {writing_agent.name}, {analysis_agent.name}")
    print(f"- Total handoff connections: {sum(len([t for t in agent.tools if isinstance(t, HandoffTool)]) for agent in [research_agent, writing_agent, analysis_agent, orchestrator])}")


if __name__ == "__main__":
    print("🚀 Starting Simple Multi-Agent System Demo")
    asyncio.run(main()) 