"""Handoff Tool for multi-agent coordination."""

import asyncio
from typing import Any, Dict, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime

from .base import Tool

if TYPE_CHECKING:
    from ..agents.agent import Agent


@dataclass
class HandoffContext:
    """Context information for agent handoffs."""
    from_agent: str
    to_agent: str
    instructions: str
    context: str
    timestamp: datetime
    handoff_chain: list


class HandoffTool(Tool):
    """Tool that allows an agent to hand off control to another agent."""
    
    def __init__(self, target_agent: 'Agent', context_filter=None):
        """Initialize handoff tool.
        
        Args:
            target_agent: The agent to hand off to
            context_filter: Optional function to filter context before handoff
        """
        self.target_agent = target_agent
        self.context_filter = context_filter
        
        # Generate tool name and description
        agent_name_clean = target_agent.name.lower().replace(' ', '_').replace('-', '_')
        
        super().__init__(
            name=f"transfer_to_{agent_name_clean}",
            description=f"Hand off the conversation to {target_agent.name}. Use when you need: {target_agent.description}",
            input_schema={
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "string",
                        "description": "Clear instructions for what the next agent should do"
                    },
                    "context": {
                        "type": "string", 
                        "description": "Important context and information to pass to the next agent"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why you're handing off to this agent"
                    }
                },
                "required": ["instructions", "reason"]
            }
        )
    
    async def execute(self, instructions: str, reason: str, context: str = "") -> str:
        """Execute the handoff to the target agent."""
        
        # Create handoff context
        handoff_context = HandoffContext(
            from_agent=getattr(self, '_current_agent_name', 'Unknown'),
            to_agent=self.target_agent.name,
            instructions=instructions,
            context=context,
            timestamp=datetime.now(),
            handoff_chain=getattr(self, '_handoff_chain', [])
        )
        
        # Beautiful logging for handoff initiation
        self._log_handoff_start(handoff_context, reason)
        
        # Prepare handoff message
        handoff_message = self._prepare_handoff_message(handoff_context)
        
        # Apply context filter if provided
        if self.context_filter:
            handoff_message = self.context_filter(handoff_message, handoff_context)
        
        try:
            # Execute the handoff
            result = await self.target_agent.run_async(handoff_message)
            
            # Log successful handoff completion
            self._log_handoff_success(handoff_context)
            
            # Format the result for the calling agent
            return self._format_handoff_result(result, handoff_context)
            
        except Exception as e:
            # Log handoff failure
            self._log_handoff_error(handoff_context, e)
            return f"❌ Handoff to {self.target_agent.name} failed: {str(e)}"
    
    def _prepare_handoff_message(self, handoff_context: HandoffContext) -> str:
        """Prepare the message for the target agent."""
        
        handoff_chain_str = " → ".join(handoff_context.handoff_chain + [handoff_context.from_agent])
        
        message = f"""🔄 **AGENT HANDOFF**
        
**From:** {handoff_context.from_agent}
**Chain:** {handoff_chain_str} → {handoff_context.to_agent}
**Time:** {handoff_context.timestamp.strftime('%H:%M:%S')}

**Instructions:** {handoff_context.instructions}"""
        
        if handoff_context.context:
            message += f"\n\n**Context:** {handoff_context.context}"
        
        message += f"\n\n**Your turn!** Please continue from here as {handoff_context.to_agent}."
        
        return message
    
    def _format_handoff_result(self, result: Any, handoff_context: HandoffContext) -> str:
        """Format the result from the target agent."""
        
        # Extract text content from the result
        if hasattr(result, 'content'):
            # Claude API response object
            content_parts = []
            for part in result.content:
                if hasattr(part, 'text'):
                    content_parts.append(part.text)
            result_text = "\n".join(content_parts)
        elif isinstance(result, str):
            result_text = result
        else:
            result_text = str(result)
        
        return f"""✅ **{handoff_context.to_agent} completed the task:**

{result_text}

---
*Handoff completed at {datetime.now().strftime('%H:%M:%S')}*"""
    
    def _log_handoff_start(self, handoff_context: HandoffContext, reason: str):
        """Log the start of a handoff with beautiful formatting."""
        
        chain_display = " → ".join(handoff_context.handoff_chain + [handoff_context.from_agent, handoff_context.to_agent])
        
        print(f"\n{'='*80}")
        print(f"🔄 **AGENT HANDOFF INITIATED**")
        print(f"{'='*80}")
        print(f"📅 Time: {handoff_context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏃 From: {handoff_context.from_agent}")
        print(f"🎯 To: {handoff_context.to_agent}")
        print(f"🔗 Chain: {chain_display}")
        print(f"💡 Reason: {reason}")
        print(f"📋 Instructions: {handoff_context.instructions}")
        if handoff_context.context:
            print(f"📝 Context: {handoff_context.context[:100]}{'...' if len(handoff_context.context) > 100 else ''}")
        print(f"{'='*80}")
    
    def _log_handoff_success(self, handoff_context: HandoffContext):
        """Log successful completion of handoff."""
        
        duration = (datetime.now() - handoff_context.timestamp).total_seconds()
        
        print(f"\n{'='*80}")
        print(f"✅ **HANDOFF COMPLETED SUCCESSFULLY**")
        print(f"{'='*80}")
        print(f"🎯 Agent: {handoff_context.to_agent}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🔙 Returning control to: {handoff_context.from_agent}")
        print(f"{'='*80}")
    
    def _log_handoff_error(self, handoff_context: HandoffContext, error: Exception):
        """Log handoff failure."""
        
        print(f"\n{'='*80}")
        print(f"❌ **HANDOFF FAILED**")
        print(f"{'='*80}")
        print(f"🎯 Target Agent: {handoff_context.to_agent}")
        print(f"⚠️  Error: {str(error)}")
        print(f"🔙 Returning control to: {handoff_context.from_agent}")
        print(f"{'='*80}")
    
    def set_current_agent(self, agent_name: str):
        """Set the current agent name for logging purposes."""
        self._current_agent_name = agent_name
    
    def set_handoff_chain(self, chain: list):
        """Set the handoff chain for tracking."""
        self._handoff_chain = chain.copy()


class HandoffLogger:
    """Utility class for enhanced handoff logging."""
    
    @staticmethod
    def log_agent_startup(agent_name: str, tools_count: int, handoff_targets: list):
        """Log when an agent starts up with handoff capabilities."""
        
        print(f"\n{'='*60}")
        print(f"🚀 **{agent_name.upper()} AGENT READY**")
        print(f"{'='*60}")
        print(f"🛠️  Total Tools: {tools_count}")
        if handoff_targets:
            print(f"🔗 Can handoff to: {', '.join(handoff_targets)}")
        else:
            print(f"🔗 No handoff targets configured")
        print(f"{'='*60}")
    
    @staticmethod
    def log_multi_agent_system_startup(agents: dict):
        """Log the startup of the entire multi-agent system."""
        
        print(f"\n{'='*80}")
        print(f"🌟 **MULTI-AGENT SYSTEM INITIALIZED**")
        print(f"{'='*80}")
        print(f"📊 Total Agents: {len(agents)}")
        
        for agent_name, agent in agents.items():
            handoff_tools = [tool for tool in agent.tools if isinstance(tool, HandoffTool)]
            handoff_targets = [tool.target_agent.name for tool in handoff_tools]
            print(f"  🤖 {agent_name}: {agent.description}")
            if handoff_targets:
                print(f"     └─ Can handoff to: {', '.join(handoff_targets)}")
            else:
                print(f"     └─ No handoff capabilities")
        
        print(f"{'='*80}")
        print(f"🎯 System ready for multi-agent coordination!")
        print(f"{'='*80}") 