#!/usr/bin/env python3
"""
Quick Multi-Agent Setup Demo - No API calls needed

Shows that the handoff system is properly configured and ready to use.
"""

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


def main():
    """Demonstrate multi-agent setup without API calls."""
    
    print("🚀 Multi-Agent System Setup Demo")
    print("="*60)
    
    # Create specialized agents
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
    
    analyst = Agent(
        name="Analysis Agent",
        description="I analyze data and provide insights",
        verbose=True
    )
    
    print("\n🔗 Setting up handoff connections...")
    
    # Add handoff capabilities
    researcher.tools.extend([
        HandoffTool(writer),
        HandoffTool(analyst)
    ])
    
    writer.tools.extend([
        HandoffTool(researcher),
        HandoffTool(analyst)
    ])
    
    analyst.tools.extend([
        HandoffTool(researcher),
        HandoffTool(writer)
    ])
    
    # Create orchestrator
    orchestrator = Agent(
        name="Orchestrator",
        description="Coordinates complex tasks between specialists",
        tools=[
            HandoffTool(researcher),
            HandoffTool(writer), 
            HandoffTool(analyst)
        ],
        verbose=True
    )
    
    # Set current agent names for beautiful logging
    for agent in [researcher, writer, analyst, orchestrator]:
        for tool in agent.tools:
            if isinstance(tool, HandoffTool):
                tool.set_current_agent(agent.name)
    
    print("\n✅ Multi-agent system configuration complete!")
    
    # Show system configuration
    print("\n📊 System Configuration:")
    print("="*60)
    
    agents = {
        "Orchestrator": orchestrator,
        "Research Agent": researcher,
        "Writing Agent": writer,
        "Analysis Agent": analyst
    }
    
    for name, agent in agents.items():
        handoff_tools = [tool for tool in agent.tools if isinstance(tool, HandoffTool)]
        handoff_targets = [tool.target_agent.name for tool in handoff_tools]
        
        print(f"\n🤖 {name}:")
        print(f"   📝 Description: {agent.description}")
        print(f"   🛠️  Total Tools: {len(agent.tools)}")
        print(f"   🔗 Can handoff to: {', '.join(handoff_targets) if handoff_targets else 'None'}")
    
    print("\n" + "="*60)
    print("🎯 Ready for Multi-Agent Coordination!")
    print("="*60)
    
    print("\n💡 To run with actual AI agents, use:")
    print("   python examples/handoff_basics.py      # Basic handoff demo")
    print("   python examples/simple_multi_agent.py  # Full multi-agent demo")
    print("   python run_example.py                  # Complete examples")


if __name__ == "__main__":
    main() 