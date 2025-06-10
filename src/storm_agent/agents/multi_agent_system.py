"""Multi-Agent System with Handoff Capabilities."""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .agent import Agent
from ..tools.handoff import HandoffTool, HandoffLogger
from ..tools.approval import RequestApprovalTool


class MultiAgentSystem:
    """Orchestrates multiple specialized agents with handoff capabilities."""
    
    def __init__(self, verbose: bool = True):
        """Initialize the multi-agent system.
        
        Args:
            verbose: Whether to enable beautiful logging
        """
        self.verbose = verbose
        self.agents: Dict[str, Agent] = {}
        self.orchestrator: Optional[Agent] = None
        
        # Initialize the system
        self._create_specialized_agents()
        self._setup_handoff_connections()
        self._create_orchestrator()
        
        if self.verbose:
            HandoffLogger.log_multi_agent_system_startup(self.agents)
    
    def _create_specialized_agents(self):
        """Create specialized agents for different tasks."""
        
        # Research Specialist - Deep research and analysis
        self.agents['research'] = Agent(
            name="Research Specialist",
            description="Expert in deep research, fact-finding, and comprehensive analysis. I gather information from multiple sources and synthesize insights.",
            enable_web_search=True,
            max_iterations=15,
            verbose=self.verbose,
            tools=[RequestApprovalTool()],  # Add approval tool
            system_prompt="""You are a Research Specialist, an expert researcher powered by Claude.

You excel at:
- Conducting thorough research on complex topics
- Finding reliable sources and verifying information  
- Analyzing data and extracting key insights
- Synthesizing information from multiple sources
- Fact-checking and validation

When you receive a research task:
1. Break down the research question into key components
2. Use web search tools to gather comprehensive information
3. Analyze and synthesize the findings
4. Present well-structured insights with sources

If you need help with writing a report or document, hand off to the Writing Specialist.
If you need help with data analysis or complex reasoning, hand off to the Analysis Specialist."""
        )
        
        # Writing Specialist - Content creation and editing
        self.agents['writing'] = Agent(
            name="Writing Specialist", 
            description="Expert in content creation, editing, and communication. I craft clear, engaging, and well-structured written content.",
            verbose=self.verbose,
            tools=[RequestApprovalTool()],  # Add approval tool
            system_prompt="""You are a Writing Specialist, an expert content creator powered by Claude.

You excel at:
- Creating clear, engaging, and well-structured content
- Editing and improving existing text
- Adapting writing style for different audiences
- Organizing information into compelling narratives
- Technical writing and documentation

When you receive a writing task:
1. Understand the purpose, audience, and requirements
2. Structure the content logically
3. Write clear, engaging prose
4. Edit and refine for clarity and impact

If you need more information or research, hand off to the Research Specialist.
If you need help with data analysis or complex calculations, hand off to the Analysis Specialist."""
        )
        
        # Analysis Specialist - Data analysis and reasoning
        self.agents['analysis'] = Agent(
            name="Analysis Specialist",
            description="Expert in data analysis, logical reasoning, and problem-solving. I break down complex problems and provide insights.",
            verbose=self.verbose,
            tools=[RequestApprovalTool()],  # Add approval tool
            system_prompt="""You are an Analysis Specialist, an expert analyst powered by Claude.

You excel at:
- Breaking down complex problems into manageable parts
- Logical reasoning and critical thinking
- Data analysis and pattern recognition
- Drawing insights from information
- Problem-solving and solution development

When you receive an analysis task:
1. Understand the problem or data
2. Apply appropriate analytical frameworks
3. Identify patterns, trends, and insights
4. Draw logical conclusions
5. Provide actionable recommendations

If you need more data or research, hand off to the Research Specialist.
If you need help presenting your analysis in written form, hand off to the Writing Specialist."""
        )
        
        # Validation Specialist - Quality control and fact-checking
        self.agents['validation'] = Agent(
            name="Validation Specialist",
            description="Expert in quality assurance, fact-checking, and validation. I ensure accuracy and quality of work.",
            enable_web_search=True,
            verbose=self.verbose,
            tools=[RequestApprovalTool()],  # Add approval tool
            system_prompt="""You are a Validation Specialist, an expert in quality assurance powered by Claude.

You excel at:
- Fact-checking and verification
- Quality assurance and review
- Identifying errors and inconsistencies
- Ensuring accuracy and reliability
- Final validation before delivery

When you receive a validation task:
1. Carefully review the content or analysis
2. Check facts and verify claims
3. Look for logical inconsistencies
4. Ensure quality and completeness
5. Provide feedback and recommendations

If you find issues that need more research, hand off to the Research Specialist.
If content needs rewriting or editing, hand off to the Writing Specialist.
If analysis needs refinement, hand off to the Analysis Specialist."""
        )
        
        if self.verbose:
            for name, agent in self.agents.items():
                HandoffLogger.log_agent_startup(
                    agent_name=agent.name,
                    tools_count=len(agent.tools),
                    handoff_targets=[]  # Will be populated after connections
                )
    
    def _setup_handoff_connections(self):
        """Set up handoff connections between agents."""
        
        # Research Specialist can handoff to Writing and Analysis
        research_handoffs = [
            HandoffTool(self.agents['writing']),
            HandoffTool(self.agents['analysis']),
            HandoffTool(self.agents['validation'])
        ]
        self.agents['research'].tools.extend(research_handoffs)
        
        # Writing Specialist can handoff to Research and Analysis  
        writing_handoffs = [
            HandoffTool(self.agents['research']),
            HandoffTool(self.agents['analysis']),
            HandoffTool(self.agents['validation'])
        ]
        self.agents['writing'].tools.extend(writing_handoffs)
        
        # Analysis Specialist can handoff to Research and Writing
        analysis_handoffs = [
            HandoffTool(self.agents['research']),
            HandoffTool(self.agents['writing']),
            HandoffTool(self.agents['validation'])
        ]
        self.agents['analysis'].tools.extend(analysis_handoffs)
        
        # Validation Specialist can handoff to all others
        validation_handoffs = [
            HandoffTool(self.agents['research']),
            HandoffTool(self.agents['writing']),
            HandoffTool(self.agents['analysis'])
        ]
        self.agents['validation'].tools.extend(validation_handoffs)
        
        # Set current agent names on handoff tools for logging
        for agent_name, agent in self.agents.items():
            for tool in agent.tools:
                if isinstance(tool, HandoffTool):
                    tool.set_current_agent(agent.name)
    
    def _create_orchestrator(self):
        """Create the main orchestrator agent."""
        
        # Create handoff tools for all specialized agents
        orchestrator_handoffs = [
            HandoffTool(self.agents['research']),
            HandoffTool(self.agents['writing']),
            HandoffTool(self.agents['analysis']),
            HandoffTool(self.agents['validation'])
        ]
        
        # Add approval tool to orchestrator tools
        orchestrator_tools = orchestrator_handoffs + [RequestApprovalTool()]
        
        self.orchestrator = Agent(
            name="Task Orchestrator",
            description="Master coordinator that analyzes complex tasks and delegates to appropriate specialists",
            tools=orchestrator_tools,
            enable_web_search=True,  # Can also do basic tasks
            max_iterations=20,
            verbose=self.verbose,
            system_prompt="""You are the Task Orchestrator, a master coordinator powered by Claude.

You are responsible for:
- Analyzing complex user requests
- Breaking down tasks into manageable components  
- Delegating to appropriate specialist agents
- Coordinating multi-step workflows
- Synthesizing results from multiple agents
- Ensuring high-quality final deliverables

**Available Specialists:**
- **Research Specialist**: Deep research, fact-finding, information gathering
- **Writing Specialist**: Content creation, editing, documentation
- **Analysis Specialist**: Data analysis, logical reasoning, problem-solving  
- **Validation Specialist**: Quality assurance, fact-checking, final review

**Decision Framework:**
1. **For research tasks**: Use Research Specialist
2. **For writing tasks**: Use Writing Specialist  
3. **For analysis/reasoning**: Use Analysis Specialist
4. **For quality review**: Use Validation Specialist
5. **For complex multi-step tasks**: Coordinate between multiple specialists

**Workflow Patterns:**
- **Research → Writing**: Research then create content
- **Research → Analysis → Writing**: Research, analyze, then document
- **Any task → Validation**: Always consider final validation for important work
- **Analysis → Writing → Validation**: Complex analysis with documented results

Always consider the best specialist for each task component and coordinate handoffs effectively."""
        )
        
        # Set current agent name on orchestrator's handoff tools
        for tool in self.orchestrator.tools:
            if isinstance(tool, HandoffTool):
                tool.set_current_agent(self.orchestrator.name)
        
        # Add orchestrator to agents dict
        self.agents['orchestrator'] = self.orchestrator
    
    async def run(self, user_input: str, **kwargs) -> Any:
        """Run a task through the multi-agent system.
        
        Args:
            user_input: The user's request
            **kwargs: Additional arguments
            
        Returns:
            The final result from the orchestrator
        """
        if self.verbose:
            self._log_task_start(user_input)
        
        try:
            result = await self.orchestrator.run_async(user_input, **kwargs)
            
            if self.verbose:
                self._log_task_completion(user_input)
            
            return result
            
        except Exception as e:
            if self.verbose:
                self._log_task_error(user_input, e)
            raise
    
    def _log_task_start(self, user_input: str):
        """Log the start of a multi-agent task."""
        
        print(f"\n{'='*100}")
        print(f"🚀 **MULTI-AGENT TASK INITIATED**")
        print(f"{'='*100}")
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Task: {user_input}")
        print(f"🤖 Orchestrator: {self.orchestrator.name}")
        print(f"👥 Available Specialists: {', '.join([agent.name for name, agent in self.agents.items() if name != 'orchestrator'])}")
        print(f"{'='*100}")
    
    def _log_task_completion(self, user_input: str):
        """Log successful task completion."""
        
        print(f"\n{'='*100}")
        print(f"✅ **MULTI-AGENT TASK COMPLETED**")
        print(f"{'='*100}")
        print(f"🎯 Task: {user_input}")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎉 Multi-agent coordination successful!")
        print(f"{'='*100}")
    
    def _log_task_error(self, user_input: str, error: Exception):
        """Log task failure."""
        
        print(f"\n{'='*100}")
        print(f"❌ **MULTI-AGENT TASK FAILED**")
        print(f"{'='*100}")
        print(f"🎯 Task: {user_input}")
        print(f"⚠️  Error: {str(error)}")
        print(f"📅 Failed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*100}")
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get a specific agent by name.
        
        Args:
            name: Agent name ('orchestrator', 'research', 'writing', 'analysis', 'validation')
            
        Returns:
            The requested agent or None if not found
        """
        return self.agents.get(name)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of the multi-agent system.
        
        Returns:
            Dictionary with system information
        """
        return {
            "total_agents": len(self.agents),
            "agents": {
                name: {
                    "name": agent.name,
                    "description": agent.description,
                    "total_tools": len(agent.tools),
                    "handoff_targets": [
                        tool.target_agent.name 
                        for tool in agent.tools 
                        if isinstance(tool, HandoffTool)
                    ]
                }
                for name, agent in self.agents.items()
            },
            "orchestrator": self.orchestrator.name if self.orchestrator else None
        } 