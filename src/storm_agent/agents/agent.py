"""Default Agent implementation with configurable tools and behavior."""

from typing import List, Optional, Any, Dict, AsyncGenerator
from anthropic import Anthropic

from .base import BaseAgent, ModelConfig
from ..utils.message_history import MessageHistory


class Agent(BaseAgent):
    """A configurable AI agent that can be customized with tools and behavior at initialization."""
    
    def __init__(
        self,
        name: str = "Agent",
        description: str = "A configurable AI assistant",
        system_prompt: Optional[str] = None,
        tools: Optional[List['Tool']] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        
        # Common tool flags
        enable_web_search: bool = False,
        
        # Execution settings
        max_iterations: int = 10,
        parallel_tools: bool = True,
        
        # Base agent parameters
        config: Optional[ModelConfig] = None,
        client: Optional[Anthropic] = None,
        verbose: bool = False,
        
        # Message settings
        message_params: Optional[Dict[str, Any]] = None,
        enable_message_history: bool = True,
        
        **kwargs
    ):
        """Initialize the configurable Agent.
        
        Args:
            name: Name of the agent
            description: Description of what the agent does
            system_prompt: Custom system prompt
            tools: List of custom tools
            mcp_servers: List of MCP server configurations
            enable_web_search: Whether to enable web search and content extraction tools
            max_iterations: Maximum iterations for tool execution loops
            parallel_tools: Whether to execute tools in parallel
            config: Model configuration
            client: Anthropic client instance
            verbose: Whether to print verbose output
            message_params: Additional parameters for message creation
            enable_message_history: Whether to enable message history
            **kwargs: Additional arguments
        """
        # Store settings for later use
        self.max_iterations = max_iterations
        self.parallel_tools = parallel_tools
        self.message_params = message_params or {}
        self.enable_message_history = enable_message_history
        
        # Prepare tools first (before calling parent constructor)
        all_tools = self._prepare_tools(tools, enable_web_search, verbose)
        
        # Generate system prompt if not provided
        final_system_prompt = system_prompt or self._generate_default_system_prompt(name, description, all_tools)
        
        # Initialize base agent
        super().__init__(
            name=name,
            description=description,
            system_prompt=final_system_prompt,
            tools=all_tools,
            mcp_servers=mcp_servers,
            config=config,
            client=client,
            verbose=verbose
        )
        
        # Initialize message history if enabled
        if self.enable_message_history:
            self.message_history = MessageHistory(
                model=self.config.model,
                system=self.system_prompt,
                client=self.client,
                enable_caching=self.config.enable_caching
            )
        else:
            self.message_history = None
    
    def _prepare_tools(
        self, 
        user_tools: Optional[List['Tool']], 
        enable_web_search: bool,
        verbose: bool = False
    ) -> List['Tool']:
        """Prepare tools by combining auto-loaded and user-provided tools.
        
        Args:
            user_tools: User-provided tools
            enable_web_search: Whether to auto-load web search and content extraction tools
            verbose: Whether to print verbose output
            
        Returns:
            Combined list of tools
        """
        tools = []
        
        # Auto-load web research tools (search + content extraction)
        if enable_web_search:
            try:
                from ..tools.web_search import BraveSearchTool, FirecrawlContentTool
                tools.extend([BraveSearchTool(), FirecrawlContentTool()])
                if verbose:
                    print("  ✅ Auto-loaded web research tools (search + content extraction)")
            except ImportError as e:
                if verbose:
                    print(f"  ⚠️ Could not load web research tools: {e}")
        
        # Add user-provided tools
        if user_tools:
            tools.extend(user_tools)
            if verbose:
                print(f"  ✅ Added {len(user_tools)} user-provided tools")
        
        return tools
    
    def _generate_default_system_prompt(self, name: str, description: str, tools: List['Tool']) -> str:
        """Generate the default system prompt for the agent."""
        base_prompt = f"""You are {name}, an AI assistant powered by Claude.

{description}

You are designed to be helpful, harmless, and honest. You can engage in conversations, answer questions, help with tasks, and provide information on a wide variety of topics."""

        # Add tool-specific instructions if tools are available
        if tools:
            tools_descriptions = []
            has_approval_tool = False
            
            for tool in tools:
                tools_descriptions.append(f"- {tool.name}: {tool.description}")
                if tool.name == "request_approval":
                    has_approval_tool = True
            
            tools_section = f"""

You have access to the following tools:
{chr(10).join(tools_descriptions)}

When you need to use a tool, use the appropriate function calling format.
Always think step by step and use tools when they would be helpful to complete the user's request.
Be efficient and avoid unnecessary tool calls."""

            # Add approval instructions if the approval tool is available
            if has_approval_tool:
                approval_section = """

**Human Approval Guidelines:**
You have access to a request_approval tool. Use this tool when you think an operation should require human oversight, such as:

- Before accessing external services or APIs that might incur costs
- Before performing operations that access personal data (like Google Drive)
- Before conducting expensive research or analysis
- Before performing operations that might take a significant amount of time
- When you're unsure if the user wants to proceed with a potentially costly or sensitive operation

Example usage:
request_approval(
    operation_description="Search the user's Google Drive for documents containing 'project budget'",
    reason="This will access personal Google Drive data"
)

Only proceed with sensitive or costly operations if you receive "APPROVED" in the response."""
                tools_section += approval_section

            base_prompt += tools_section
        
        return base_prompt
    
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for the agent. This should not be called for Agent class."""
        # This method shouldn't be called for the Agent class since we handle system prompt generation differently
        return self._generate_default_system_prompt(self.name, self.description, self.tools)
    
    def _prepare_message_params(self) -> Dict[str, Any]:
        """Prepare parameters for the Claude API message."""
        params = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self.system_prompt,
        }
        
        # Add tools if available
        if self.tools:
            params["tools"] = self._prepare_tools_for_api()
        
        # Add messages if message history is enabled
        if self.message_history:
            params["messages"] = self.message_history.format_for_api()
        else:
            # For stateless operation, just include the current conversation
            params["messages"] = getattr(self, '_current_messages', [])
        
        # Add any additional message parameters
        params.update(self.message_params)
        
        return params
    
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
        
        if self.verbose:
            print(f"\n🤖 {self.name} received: {user_input}")
        
        # Add user message to history if enabled
        if self.message_history:
            await self.message_history.add_message("user", user_input)
        else:
            # For stateless operation, maintain current conversation
            self._current_messages = [{"role": "user", "content": user_input}]
        
        # Route to streaming or non-streaming implementation
        if stream:
            return self._streaming_agent_loop(user_input)
        else:
            return await self._agent_loop(user_input)
    
    async def stream_async(self, user_input: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the agent's response asynchronously with user input.
        
        This method is provided for backward compatibility. For new code, 
        prefer using run_async(user_input, stream=True).
        
        Args:
            user_input: The user's input/query
            **kwargs: Additional arguments
            
        Yields:
            Dict containing streaming events with 'type' and relevant data
        """
        async for event in await self.run_async(user_input, stream=True, **kwargs):
            yield event
    
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
        
        if stream:
            # For streaming, we need to collect all events synchronously
            async def _run_async_stream():
                events = []
                async for event in await self.run_async(user_input, stream=True, **kwargs):
                    events.append(event)
                return events
            
            events = asyncio.run(_run_async_stream())
            # Return an iterator over the collected events
            return iter(events)
        else:
            # For non-streaming, run normally
            return asyncio.run(self.run_async(user_input, stream=False, **kwargs))
    
    async def _agent_loop(self, user_input: str) -> Any:
        """Main agent loop for processing user input and tool calls."""
        iteration = 0
        
        while iteration < self.max_iterations:
            # Prepare message parameters
            params = self._prepare_message_params()
            
            # Get response from Claude
            response = self.client.messages.create(**params)
            
            # Add assistant message to history
            if self.message_history:
                await self.message_history.add_message(
                    "assistant", 
                    response.content,
                    usage=response.usage
                )
            
            # Check if we need to execute tools
            tool_calls = [
                content for content in response.content 
                if hasattr(content, 'type') and content.type == 'tool_use'
            ]
            
            if not tool_calls:
                # No tools to execute, return the response
                if self.verbose:
                    print(f"\n✅ {self.name} Response:")
                    print(self._format_response(response.content))
                
                return response
            
            # Execute tool calls
            if self.verbose:
                print(f"\n🔧 {self.name} is using tools (iteration {iteration + 1})...")
                for tool_call in tool_calls:
                    print(f"  - {tool_call.name}: {tool_call.input}")
            
            tool_results = await self.execute_tool_calls(tool_calls, parallel=self.parallel_tools)
            
            # Add tool results to message history
            if self.message_history:
                for result in tool_results:
                    await self.message_history.add_message("user", [result])
            else:
                # For stateless operation, add to current messages
                if not hasattr(self, '_current_messages'):
                    self._current_messages = []
                self._current_messages.append({
                    "role": "assistant", 
                    "content": response.content
                })
                for result in tool_results:
                    self._current_messages.append({
                        "role": "user",
                        "content": [result]
                    })
            
            iteration += 1
        
        # Handle max iterations reached
        if self.verbose:
            print(f"\n⚠️ Max iterations ({self.max_iterations}) reached")
        
        return response
    
    async def _streaming_agent_loop(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Main streaming agent loop for processing user input and tool calls."""
        iteration = 0
        
        while iteration < self.max_iterations:
            # Prepare message parameters
            params = self._prepare_message_params()
            params["stream"] = True  # Enable streaming
            
            # Get streaming response from Claude
            stream = self.client.messages.create(**params)
            
            # Process streaming events
            current_content = []
            current_tool_calls = []
            assistant_content_buffer = []
            
            try:
                for event in stream:
                    # Yield the raw event to the user
                    event_data = {
                        "type": "stream_event",
                        "event": event
                    }
                    yield event_data
                    
                    # Process different event types
                    if hasattr(event, 'type'):
                        if event.type == "message_start":
                            yield {
                                "type": "message_start",
                                "message": event.message
                            }
                        
                        elif event.type == "content_block_start":
                            content_block = event.content_block
                            if hasattr(content_block, 'type'):
                                if content_block.type == "text":
                                    yield {
                                        "type": "text_start",
                                        "index": event.index
                                    }
                                elif content_block.type == "tool_use":
                                    yield {
                                        "type": "tool_start",
                                        "index": event.index,
                                        "tool_name": content_block.name,
                                        "tool_id": content_block.id
                                    }
                        
                        elif event.type == "content_block_delta":
                            if hasattr(event, 'delta'):
                                if hasattr(event.delta, 'type'):
                                    if event.delta.type == "text_delta":
                                        yield {
                                            "type": "text_delta",
                                            "index": event.index,
                                            "text": event.delta.text
                                        }
                                        # Buffer text content for final response
                                        if len(assistant_content_buffer) <= event.index:
                                            assistant_content_buffer.extend([None] * (event.index + 1 - len(assistant_content_buffer)))
                                        if assistant_content_buffer[event.index] is None:
                                            assistant_content_buffer[event.index] = {"type": "text", "text": ""}
                                        assistant_content_buffer[event.index]["text"] += event.delta.text
                                    
                                    elif event.delta.type == "input_json_delta":
                                        yield {
                                            "type": "tool_input_delta",
                                            "index": event.index,
                                            "partial_json": event.delta.partial_json
                                        }
                        
                        elif event.type == "content_block_stop":
                            yield {
                                "type": "content_block_stop",
                                "index": event.index
                            }
                        
                        elif event.type == "message_delta":
                            yield {
                                "type": "message_delta",
                                "delta": event.delta,
                                "usage": getattr(event, 'usage', None)
                            }
                        
                        elif event.type == "message_stop":
                            yield {
                                "type": "message_stop"
                            }
                
                # Get the final complete response to check for tool calls
                final_response = stream.get_final_message()
                
                # Add assistant message to history
                if self.message_history:
                    await self.message_history.add_message(
                        "assistant",
                        final_response.content,
                        usage=final_response.usage
                    )
                
                # Check if we need to execute tools
                tool_calls = [
                    content for content in final_response.content
                    if hasattr(content, 'type') and content.type == 'tool_use'
                ]
                
                if not tool_calls:
                    # No tools to execute, we're done
                    if self.verbose:
                        print(f"\n✅ {self.name} streaming completed")
                    
                    yield {
                        "type": "final_response",
                        "response": final_response
                    }
                    return
                
                # Execute tool calls
                if self.verbose:
                    print(f"\n🔧 {self.name} is using tools (iteration {iteration + 1})...")
                    for tool_call in tool_calls:
                        print(f"  - {tool_call.name}: {tool_call.input}")
                
                yield {
                    "type": "tools_start",
                    "tool_calls": tool_calls,
                    "iteration": iteration + 1
                }
                
                tool_results = await self.execute_tool_calls(tool_calls, parallel=self.parallel_tools)
                
                yield {
                    "type": "tools_complete",
                    "tool_results": tool_results,
                    "iteration": iteration + 1
                }
                
                # Add tool results to message history
                if self.message_history:
                    for result in tool_results:
                        await self.message_history.add_message("user", [result])
                else:
                    # For stateless operation, add to current messages
                    if not hasattr(self, '_current_messages'):
                        self._current_messages = []
                    self._current_messages.append({
                        "role": "assistant",
                        "content": final_response.content
                    })
                    for result in tool_results:
                        self._current_messages.append({
                            "role": "user",
                            "content": [result]
                        })
                
                iteration += 1
                
            except Exception as e:
                yield {
                    "type": "error",
                    "error": str(e),
                    "iteration": iteration
                }
                break
        
        # Handle max iterations reached
        if iteration >= self.max_iterations:
            if self.verbose:
                print(f"\n⚠️ Max iterations ({self.max_iterations}) reached")
            
            yield {
                "type": "max_iterations_reached",
                "max_iterations": self.max_iterations
            }
    
    def _format_response(self, content: List[Any]) -> str:
        """Format the response content for display."""
        formatted_parts = []
        
        for part in content:
            if hasattr(part, 'text'):
                formatted_parts.append(part.text)
            elif hasattr(part, 'type') and part.type == 'tool_use':
                formatted_parts.append(f"[Using tool: {part.name}]")
        
        return "\n".join(formatted_parts)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's configuration and state."""
        summary = {
            "name": self.name,
            "description": self.description,
            "model": self.config.model,
            "tools": [tool.name for tool in self.tools],
            "max_iterations": self.max_iterations,
            "parallel_tools": self.parallel_tools,
            "message_history_enabled": self.enable_message_history
        }
        
        if self.message_history:
            summary["message_history"] = {
                "message_count": len(self.message_history.messages),
                "total_tokens": self.message_history.total_tokens
            }
        
        return summary 