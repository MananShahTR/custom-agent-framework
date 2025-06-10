"""Web Search Agent implementation."""

from typing import List, Optional, Any, Dict, Union, AsyncGenerator
from anthropic import Anthropic

from .base import BaseAgent, ModelConfig
from ..tools.web_search import BraveSearchTool, FirecrawlContentTool
from ..utils.message_history import MessageHistory


class WebSearchAgent(BaseAgent):
    """Agent specialized in web search and content extraction."""
    
    def __init__(
        self,
        name: str = "WebSearchAgent",
        system_prompt: Optional[str] = None,
        tools: Optional[List['Tool']] = None,
        config: Optional[ModelConfig] = None,
        verbose: bool = False,
        client: Optional[Anthropic] = None,
        message_params: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the WebSearchAgent.
        
        Args:
            name: Name of the agent
            system_prompt: Custom system prompt
            tools: List of tools (defaults to web search tools)
            config: Model configuration
            verbose: Whether to print verbose output
            client: Anthropic client instance
            message_params: Additional parameters for message creation
        """
        # Default tools if none provided
        if tools is None:
            tools = [BraveSearchTool(), FirecrawlContentTool()]
        
        # Initialize base agent
        super().__init__(
            name=name,
            description="An AI agent specialized in searching the web and extracting content from websites.",
            system_prompt=system_prompt,
            tools=tools,
            config=config,
            client=client,
            verbose=verbose
        )
        
        self.message_params = message_params or {}
        
        # Initialize message history
        self.message_history = MessageHistory(
            model=self.config.model,
            system=self.system_prompt,
            client=self.client,
            enable_caching=self.config.enable_caching
        )
    
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for web search agent."""
        return """You are a helpful AI assistant with access to web search and content extraction tools.

Your primary capabilities include:
1. Searching the web for current information using Brave Search
2. Extracting and reading content from web pages using Firecrawl
3. Providing comprehensive, well-researched answers based on web sources

When responding to queries:
- Use web search to find relevant and current information
- Extract content from promising URLs to get detailed information
- Synthesize information from multiple sources when appropriate
- Always cite your sources with URLs
- Be transparent about the limitations of your search results
- If search results are limited, suggest alternative search strategies

Remember to:
- Verify information across multiple sources when possible
- Prioritize recent and authoritative sources
- Clearly distinguish between facts from sources and your own analysis
- Use markdown formatting to make your responses clear and readable"""
    
    def _prepare_message_params(self) -> Dict[str, Any]:
        """Prepare parameters for the Claude API message."""
        params = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self.system_prompt,
            "tools": self._prepare_tools_for_api(),
            "messages": self.message_history.format_for_api()
        }
        
        # Add any additional message parameters
        params.update(self.message_params)
        
        return params
    
    async def run_async(self, user_input: str, stream: bool = False, **kwargs) -> Any:
        """Run the agent asynchronously with user input.
        
        Args:
            user_input: The user's input/query
            stream: Whether to stream the response (returns AsyncGenerator if True)
            **kwargs: Additional arguments
            
        Returns:
            The agent's response (Message object if stream=False, AsyncGenerator if stream=True)
        """
        # Ensure MCP tools are set up before running
        await self._ensure_mcp_setup()
        
        # Add user message to history
        await self.message_history.add_message("user", user_input)
        
        # Route to streaming or non-streaming implementation
        if stream:
            return self._streaming_agent_loop(user_input)
        else:
            # Run the agent loop
            response = await self._agent_loop(user_input)
            return response
    
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
    
    async def _streaming_agent_loop(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Main streaming agent loop for processing user input and tool calls."""
        try:
            # Prepare message parameters
            params = self._prepare_message_params()
            params["stream"] = True  # Enable streaming
            
            # Get streaming response from Claude
            stream = self.client.messages.create(**params)
            
            # Process streaming events
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
                print(f"\n🔧 {self.name} is using tools...")
                for tool_call in tool_calls:
                    print(f"   - {tool_call.name}: {tool_call.input}")
            
            yield {
                "type": "tools_start",
                "tool_calls": tool_calls
            }
            
            tool_results = await self.execute_tool_calls(tool_calls)
            
            yield {
                "type": "tools_complete",
                "tool_results": tool_results
            }
            
            # Add tool results to message history
            for result in tool_results:
                await self.message_history.add_message("user", [result])
            
            # Continue with another iteration by recursively calling this method
            # Note: WebSearchAgent has simpler iteration logic than the base Agent
            async for event in self._streaming_agent_loop(user_input):
                yield event
                
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }
    
    async def _agent_loop(self, user_input: str) -> Any:
        """Main agent loop for processing user input and tool calls."""
        while True:
            # Prepare message parameters
            params = self._prepare_message_params()
            
            # Get response from Claude
            response = self.client.messages.create(**params)
            
            # Add assistant message to history
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
                    print(f"\n{self.name} Response:")
                    print(self._format_response(response.content))
                
                return response
            
            # Execute tool calls
            if self.verbose:
                print(f"\n{self.name} is using tools...")
                for tool_call in tool_calls:
                    print(f"  - {tool_call.name}: {tool_call.input}")
            
            tool_results = await self.execute_tool_calls(tool_calls)
            
            # Add tool results to message history
            for result in tool_results:
                await self.message_history.add_message("user", [result])
            
            # Continue the loop to get the next response
    
    def _format_response(self, content: List[Any]) -> str:
        """Format the response content for display."""
        formatted_parts = []
        
        for part in content:
            if hasattr(part, 'text'):
                formatted_parts.append(part.text)
            elif hasattr(part, 'type') and part.type == 'tool_use':
                formatted_parts.append(f"[Using tool: {part.name}]")
        
        return "\n".join(formatted_parts)
    
    def search_web(self, query: str, count: int = 5) -> str:
        """Convenience method to search the web directly."""
        tool = self.tool_dict.get("brave_search")
        if tool:
            import asyncio
            return asyncio.run(tool.execute(query=query, count=count))
        return "Web search tool not available"
    
    def extract_content(self, url: str, max_length: int = 8000) -> str:
        """Convenience method to extract content from a URL directly."""
        tool = self.tool_dict.get("firecrawl_extract")
        if tool:
            import asyncio
            return asyncio.run(tool.execute(url=url, max_length=max_length))
        return "Content extraction tool not available" 