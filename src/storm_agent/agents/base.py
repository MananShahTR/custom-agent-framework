"""Base Agent class for building AI agents with Claude."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Union, AsyncGenerator, Iterator
from contextlib import AsyncExitStack
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration settings for Claude model parameters."""
    
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 1.0
    context_window_tokens: int = 180000
    enable_caching: bool = True


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List['Tool']] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        config: Optional[ModelConfig] = None,
        client: Optional[Anthropic] = None,
        verbose: bool = False
    ):
        """Initialize the agent.
        
        Args:
            name: Name of the agent
            description: Description of what the agent does
            system_prompt: System prompt for the agent
            tools: List of tools available to the agent
            mcp_servers: List of MCP server configurations
            config: Model configuration
            client: Anthropic client instance
            verbose: Whether to print verbose output
        """
        self.name = name
        self.description = description
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.tools = tools or []
        self.mcp_servers = mcp_servers or []
        self.config = config or ModelConfig()
        self.verbose = verbose
        self._mcp_setup_complete = False
        self._mcp_stack = None
        
        # Initialize Anthropic client
        self.client = client or Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "")
        )
        
        # Validate API key
        if not self.client.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please set it in your environment or .env file."
            )
        
        # Convert tools to dictionary for easy lookup
        self.tool_dict = {tool.name: tool for tool in self.tools}
        
        if self.verbose:
            print(f"✅ Initialized {self.name}")
            print(f"   Description: {self.description}")
            print(f"   Model: {self.config.model}")
            print(f"   Tools: {[tool.name for tool in self.tools]}")
            if self.mcp_servers:
                print(f"   MCP Servers: {len(self.mcp_servers)} configured")
    
    async def _ensure_mcp_setup(self):
        """Ensure MCP tools are set up if configured."""
        if not self.mcp_servers or self._mcp_setup_complete:
            return
        
        try:
            from ..utils.connections import setup_mcp_connections
            
            # Create a long-lived AsyncExitStack for MCP connections
            self._mcp_stack = AsyncExitStack()
            await self._mcp_stack.__aenter__()
            
            mcp_tools = await setup_mcp_connections(self.mcp_servers, self._mcp_stack)
            
            # Add MCP tools to the agent permanently
            self.tools.extend(mcp_tools)
            for tool in mcp_tools:
                self.tool_dict[tool.name] = tool
            
            self._mcp_setup_complete = True
            
            if self.verbose and mcp_tools:
                print(f"✅ Loaded {len(mcp_tools)} MCP tools")
                for tool in mcp_tools:
                    print(f"   - {tool.name}: {tool.description}")
            
        except ImportError:
            if self.verbose:
                print("⚠️  MCP dependencies not installed. Install with: pip install mcp")
        except Exception as e:
            if self.verbose:
                print(f"❌ Error setting up MCP tools: {e}")
    
    async def cleanup(self):
        """Clean up MCP connections."""
        if self._mcp_stack:
            try:
                await self._mcp_stack.__aexit__(None, None, None)
            except Exception as e:
                if self.verbose:
                    print(f"Error during MCP cleanup: {e}")
            finally:
                self._mcp_stack = None
                self._mcp_setup_complete = False
    
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for the agent."""
        return f"""You are {self.name}, an AI assistant powered by Claude.

{self.description}

You have access to the following tools:
{self._format_tools_description()}

When you need to use a tool, use the appropriate function calling format.
Always think step by step and use tools when they would be helpful to complete the user's request.
"""
    
    def _format_tools_description(self) -> str:
        """Format tools description for the system prompt."""
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        
        return "\n".join(descriptions)
    
    def _prepare_tools_for_api(self) -> List[Dict[str, Any]]:
        """Prepare tools in the format expected by Claude API."""
        return [tool.to_dict() for tool in self.tools]
    
    @abstractmethod
    async def run_async(self, user_input: str, stream: bool = False, **kwargs) -> Any:
        """Run the agent asynchronously with user input.
        
        Args:
            user_input: The user's input/query
            stream: Whether to stream the response (if True, returns async generator)
            **kwargs: Additional arguments
            
        Returns:
            The agent's response (Message object if stream=False, AsyncGenerator if stream=True)
        """
        # Ensure MCP tools are set up before running
        await self._ensure_mcp_setup()
        # Implementation should be provided by subclasses
        pass
    
    @abstractmethod
    async def stream_async(self, user_input: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the agent's response asynchronously with user input.
        
        Args:
            user_input: The user's input/query
            **kwargs: Additional arguments
            
        Yields:
            Dict containing streaming events with 'type' and relevant data
        """
        # Ensure MCP tools are set up before running
        await self._ensure_mcp_setup()
        # Implementation should be provided by subclasses
        pass
    
    def run(self, user_input: str, stream: bool = False, **kwargs) -> Any:
        """Run the agent synchronously with user input.
        
        Args:
            user_input: The user's input/query
            stream: Whether to stream the response (if True, returns Iterator)
            **kwargs: Additional arguments
            
        Returns:
            The agent's response (Message object if stream=False, Iterator if stream=True)
        """
        import asyncio
        return asyncio.run(self.run_async(user_input, stream=stream, **kwargs))
    
    def stream(self, user_input: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """Stream the agent's response synchronously with user input.
        
        Args:
            user_input: The user's input/query
            **kwargs: Additional arguments
            
        Yields:
            Dict containing streaming events with 'type' and relevant data
        """
        import asyncio
        
        async def _async_generator():
            async for event in self.stream_async(user_input, **kwargs):
                yield event
        
        async def _run_async_generator():
            events = []
            async for event in _async_generator():
                events.append(event)
            return events
        
        events = asyncio.run(_run_async_generator())
        for event in events:
            yield event

    async def execute_tool_calls(
        self, 
        tool_calls: List[Any], 
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """Execute tool calls from Claude's response.
        
        Args:
            tool_calls: List of tool calls from Claude
            parallel: Whether to execute tools in parallel
            
        Returns:
            List of tool results
        """
        import asyncio
        
        async def _execute_single_tool(call: Any) -> Dict[str, Any]:
            tool_name = call.name
            tool_args = call.input
            
            if tool_name not in self.tool_dict:
                return {
                    "tool_use_id": call.id,
                    "type": "tool_result",
                    "content": f"Error: Tool '{tool_name}' not found",
                    "is_error": True
                }
            
            try:
                tool = self.tool_dict[tool_name]
                result = await tool.execute(**tool_args)
                
                return {
                    "tool_use_id": call.id,
                    "type": "tool_result",
                    "content": result
                }
            except Exception as e:
                return {
                    "tool_use_id": call.id,
                    "type": "tool_result",
                    "content": f"Error executing {tool_name}: {str(e)}",
                    "is_error": True
                }
        
        if parallel:
            # Execute all tools in parallel
            tasks = [_execute_single_tool(call) for call in tool_calls]
            results = await asyncio.gather(*tasks)
        else:
            # Execute tools sequentially
            results = []
            for call in tool_calls:
                result = await _execute_single_tool(call)
                results.append(result)
        
        return results
    
    def __del__(self):
        """Cleanup when agent is destroyed."""
        if self._mcp_stack:
            # Note: This is a fallback cleanup, ideally cleanup() should be called explicitly
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule cleanup for later
                    loop.create_task(self.cleanup())
                else:
                    # If loop is not running, run cleanup directly
                    loop.run_until_complete(self.cleanup())
            except Exception:
                # Silent cleanup failure
                pass 