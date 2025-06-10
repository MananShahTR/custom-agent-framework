"""Web Search Agent implementation with Claude API, Brave Search, and Firecrawl tools."""

import asyncio
import os
import json
import requests
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Union
from urllib.parse import urlencode, urlparse

from anthropic import Anthropic
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration settings for Claude model parameters."""
    
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 1.0
    context_window_tokens: int = 180000


@dataclass
class Tool:
    """Base class for all agent tools."""
    
    name: str
    description: str
    input_schema: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert tool to Claude API format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
    
    async def execute(self, **kwargs) -> str:
        """Execute the tool with provided parameters."""
        raise NotImplementedError(
            "Tool subclasses must implement execute method"
        )


class BraveSearchTool(Tool):
    """Tool for performing web searches using Brave Search API."""
    
    def __init__(self):
        super().__init__(
            name="brave_search",
            description="Search the web for current information using Brave Search API. Returns high-quality, recent search results with snippets and URLs.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information about"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of search results to return (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip (default: 0)",
                        "default": 0,
                        "minimum": 0
                    },
                    "country": {
                        "type": "string",
                        "description": "Country code for localized results (e.g., 'US', 'GB', 'CA')",
                        "default": "US"
                    }
                },
                "required": ["query"]
            }
        )
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: BRAVE_SEARCH_API_KEY not found. Falling back to basic search.")
    
    async def execute(self, query: str, count: int = 5, offset: int = 0, country: str = "US") -> str:
        """Execute web search using Brave Search API."""
        if not self.api_key:
            return await self._fallback_search(query)
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            # Use only essential, well-supported parameters
            params = {
                "q": query,
                "count": min(count, 20),
                "country": country,
                "search_lang": "en"
            }
            
            # Add offset only if it's greater than 0
            if offset > 0:
                params["offset"] = offset
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Process web results
            web_results = data.get("web", {}).get("results", [])
            for result in web_results[:count]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "published": result.get("published", ""),
                    "type": "web"
                })
            
            # Add news results if available
            news_results = data.get("news", {}).get("results", [])
            for result in news_results[:min(2, count - len(results))]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "published": result.get("age", ""),
                    "type": "news"
                })
            
            if not results:
                return await self._fallback_search(query)
            
            # Format results
            formatted_results = f"🔍 Brave Search results for: **{query}**\n\n"
            
            for i, result in enumerate(results, 1):
                icon = "📰" if result["type"] == "news" else "🌐"
                formatted_results += f"{i}. {icon} **{result['title']}**\n"
                if result['description']:
                    formatted_results += f"   {result['description']}\n"
                formatted_results += f"   🔗 URL: {result['url']}\n"
                if result['published']:
                    formatted_results += f"   📅 Published: {result['published']}\n"
                formatted_results += "\n"
            
            return formatted_results
            
        except requests.RequestException as e:
            error_msg = f"❌ Error performing Brave search: {str(e)}"
            if "422" in str(e):
                error_msg += "\n   This might be due to API parameter restrictions. Using fallback search..."
            elif "401" in str(e):
                error_msg += "\n   Check if your BRAVE_SEARCH_API_KEY is valid."
            elif "429" in str(e):
                error_msg += "\n   Rate limit exceeded. Please wait before trying again."
            
            print(error_msg)
            return await self._fallback_search(query)
        except Exception as e:
            print(f"❌ Unexpected error in Brave search: {str(e)}")
            return await self._fallback_search(query)
    
    async def _fallback_search(self, query: str) -> str:
        """Fallback search method when Brave API is not available."""
        try:
            # Use DuckDuckGo as fallback
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Check for instant answer
            if data.get('Answer'):
                results.append({
                    'title': 'Instant Answer',
                    'content': data['Answer'],
                    'url': data.get('AnswerURL', '')
                })
            
            # Check for abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Abstract'),
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', '')
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0],
                        'content': topic.get('Text', ''),
                        'url': topic.get('FirstURL', '')
                    })
            
            if results:
                formatted_results = f"🔍 Fallback search results for: **{query}**\n\n"
                for i, result in enumerate(results, 1):
                    formatted_results += f"{i}. **{result['title']}**\n"
                    formatted_results += f"   {result['content']}\n"
                    if result['url']:
                        formatted_results += f"   🔗 URL: {result['url']}\n"
                    formatted_results += "\n"
                return formatted_results
            else:
                return f"🔍 Search completed for '{query}'. Limited results available. Consider searching manually on search engines for more current information."
                
        except Exception as e:
            return f"❌ Error in fallback search: {str(e)}"


class FirecrawlContentTool(Tool):
    """Tool for extracting clean, readable content from URLs using Firecrawl."""
    
    def __init__(self):
        super().__init__(
            name="firecrawl_extract",
            description="Extract clean, readable content from web pages using Firecrawl. Returns markdown-formatted content with improved text extraction.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to extract content from"
                    },
                    "formats": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["markdown", "html", "rawHtml"]},
                        "description": "Output formats to include (default: ['markdown'])",
                        "default": ["markdown"]
                    },
                    "include_tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "HTML tags to include (e.g., ['h1', 'h2', 'p', 'a'])",
                        "default": ["h1", "h2", "h3", "p", "a", "ul", "ol", "li"]
                    },
                    "exclude_tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "HTML tags to exclude (e.g., ['nav', 'footer', 'sidebar'])",
                        "default": ["nav", "footer", "header", "sidebar", "ads"]
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum content length in characters (default: 8000)",
                        "default": 8000,
                        "minimum": 500,
                        "maximum": 50000
                    }
                },
                "required": ["url"]
            }
        )
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl = None
        if self.api_key:
            try:
                self.firecrawl = FirecrawlApp(api_key=self.api_key)
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Firecrawl: {str(e)}")
        else:
            print("⚠️  Warning: FIRECRAWL_API_KEY not found. Falling back to basic extraction.")
    
    async def execute(
        self, 
        url: str, 
        formats: List[str] = None, 
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        max_length: int = 8000
    ) -> str:
        """Extract content from URL using Firecrawl or fallback method."""
        
        if formats is None:
            formats = ["markdown"]
        if include_tags is None:
            include_tags = ["h1", "h2", "h3", "p", "a", "ul", "ol", "li"]
        if exclude_tags is None:
            exclude_tags = ["nav", "footer", "header", "sidebar", "ads"]
        
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return f"❌ Invalid URL format: {url}"
        
        if self.firecrawl:
            return await self._extract_with_firecrawl(url, formats, include_tags, exclude_tags, max_length)
        else:
            return await self._extract_fallback(url, max_length)
    
    async def _extract_with_firecrawl(
        self, 
        url: str, 
        formats: List[str], 
        include_tags: List[str],
        exclude_tags: List[str],
        max_length: int
    ) -> str:
        """Extract content using Firecrawl API."""
        try:
            # Configure scraping options - use the correct parameter structure
            scrape_options = {
                "formats": formats,
                "includeTags": include_tags,
                "excludeTags": exclude_tags,
                "waitFor": 2000,  # Wait 2 seconds for dynamic content
                "timeout": 30000   # 30 second timeout
            }
            
            # Scrape the URL with correct parameter structure
            result = self.firecrawl.scrape_url(url, **scrape_options)
            
            # Handle different response types from Firecrawl
            if hasattr(result, 'success') and not result.success:
                error_msg = getattr(result, 'error', 'Unknown error')
                return f"❌ Firecrawl extraction failed for {url}: {error_msg}"
            elif hasattr(result, 'get') and not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                return f"❌ Firecrawl extraction failed for {url}: {error_msg}"
            
            # Extract data from response
            if hasattr(result, 'data'):
                data = result.data
            elif hasattr(result, 'get'):
                data = result.get("data", {})
            else:
                data = result
            
            # Get content in order of preference
            content = ""
            if hasattr(data, 'markdown') and data.markdown:
                content = data.markdown
            elif hasattr(data, 'html') and data.html:
                content = data.html
            elif hasattr(data, 'get'):
                content = data.get("markdown") or data.get("html") or data.get("rawHtml", "")
            
            if not content:
                return f"❌ No content extracted from {url}"
            
            # Get metadata
            metadata = {}
            if hasattr(data, 'metadata'):
                metadata = data.metadata if hasattr(data.metadata, '__dict__') else data.metadata
            elif hasattr(data, 'get'):
                metadata = data.get("metadata", {})
            
            title = ""
            description = ""
            if hasattr(metadata, 'title'):
                title = metadata.title
            elif isinstance(metadata, dict):
                title = metadata.get("title", "")
                
            if hasattr(metadata, 'description'):
                description = metadata.description
            elif isinstance(metadata, dict):
                description = metadata.get("description", "")
            
            # Format the response
            response = f"🔥 **Firecrawl Content Extraction**\n"
            response += f"📋 **URL:** {url}\n"
            if title:
                response += f"📄 **Title:** {title}\n"
            if description:
                response += f"📝 **Description:** {description}\n"
            response += f"\n---\n\n"
            
            # Truncate content if too long
            if len(content) > max_length:
                content = content[:max_length] + "\n\n... (content truncated)"
            
            response += content
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error with Firecrawl extraction: {str(e)}"
            if "400" in str(e):
                error_msg += "\n   Bad request - checking API parameters..."
            elif "401" in str(e):
                error_msg += "\n   Check if your FIRECRAWL_API_KEY is valid."
            elif "429" in str(e):
                error_msg += "\n   Rate limit exceeded. Please wait before trying again."
            
            print(error_msg)
            return await self._extract_fallback(url, max_length)
    
    async def _extract_fallback(self, url: str, max_length: int) -> str:
        """Fallback content extraction using requests and BeautifulSoup."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "sidebar", "aside", "ads"]):
                element.decompose()
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract meta description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Extract main content
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '.post-content', 
                '.entry-content', '.article-content', '#content', '.main-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extract text content
            content_text = main_content.get_text(separator='\n', strip=True)
            
            # Clean up the text
            lines = [line.strip() for line in content_text.split('\n') if line.strip()]
            content_text = '\n'.join(lines)
            
            # Format response
            response = f"🌐 **Basic Content Extraction**\n"
            response += f"📋 **URL:** {url}\n"
            if title:
                response += f"📄 **Title:** {title}\n"
            if description:
                response += f"📝 **Description:** {description}\n"
            response += f"\n---\n\n"
            
            # Truncate if too long
            if len(content_text) > max_length:
                content_text = content_text[:max_length] + "\n\n... (content truncated)"
            
            response += content_text
            
            return response
            
        except Exception as e:
            return f"❌ Error extracting content from {url}: {str(e)}"


class MessageHistory:
    """Manages chat history with token tracking and context management."""
    
    def __init__(
        self,
        model: str,
        system: str,
        context_window_tokens: int,
        client: Any,
        enable_caching: bool = True,
    ):
        self.model = model
        self.system = system
        self.context_window_tokens = context_window_tokens
        self.messages: list[dict[str, Any]] = []
        self.total_tokens = 0
        self.enable_caching = enable_caching
        self.message_tokens: list[tuple[int, int]] = []
        self.client = client
        
        # Set initial total tokens to system prompt
        try:
            system_token = (
                self.client.messages.count_tokens(
                    model=self.model,
                    system=self.system,
                    messages=[{"role": "user", "content": "test"}],
                ).input_tokens
                - 1
            )
        except Exception:
            system_token = len(self.system) / 4
        
        self.total_tokens = system_token
    
    async def add_message(
        self,
        role: str,
        content: Union[str, list[dict[str, Any]]],
        usage: Optional[Any] = None,
    ):
        """Add a message to the history and track token usage."""
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        
        message = {"role": role, "content": content}
        self.messages.append(message)
        
        if role == "assistant" and usage:
            total_input = (
                usage.input_tokens
                + getattr(usage, "cache_read_input_tokens", 0)
                + getattr(usage, "cache_creation_input_tokens", 0)
            )
            output_tokens = usage.output_tokens
            
            current_turn_input = total_input - self.total_tokens
            self.message_tokens.append((current_turn_input, output_tokens))
            self.total_tokens += current_turn_input + output_tokens
    
    def truncate(self) -> None:
        """Remove oldest messages when context window limit is exceeded."""
        if self.total_tokens <= self.context_window_tokens:
            return
        
        TRUNCATION_NOTICE_TOKENS = 25
        TRUNCATION_MESSAGE = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "[Earlier history has been truncated.]",
                }
            ],
        }
        
        def remove_message_pair():
            self.messages.pop(0)
            self.messages.pop(0)
            
            if self.message_tokens:
                input_tokens, output_tokens = self.message_tokens.pop(0)
                self.total_tokens -= input_tokens + output_tokens
        
        while (
            self.message_tokens
            and len(self.messages) >= 2
            and self.total_tokens > self.context_window_tokens
        ):
            remove_message_pair()
            
            if self.messages and self.message_tokens:
                original_input_tokens, original_output_tokens = (
                    self.message_tokens[0]
                )
                self.messages[0] = TRUNCATION_MESSAGE
                self.message_tokens[0] = (
                    TRUNCATION_NOTICE_TOKENS,
                    original_output_tokens,
                )
                self.total_tokens += (
                    TRUNCATION_NOTICE_TOKENS - original_input_tokens
                )
    
    def format_for_api(self) -> list[dict[str, Any]]:
        """Format messages for Claude API with optional caching."""
        result = [
            {"role": m["role"], "content": m["content"]} for m in self.messages
        ]
        
        if self.enable_caching and self.messages:
            result[-1]["content"] = [
                {**block, "cache_control": {"type": "ephemeral"}}
                for block in self.messages[-1]["content"]
            ]
        return result


async def execute_tools(
    tool_calls: list[Any], tool_dict: dict[str, Any], parallel: bool = True
) -> list[dict[str, Any]]:
    """Execute multiple tools sequentially or in parallel."""
    
    async def _execute_single_tool(call: Any) -> dict[str, Any]:
        """Execute a single tool and handle errors."""
        response = {"type": "tool_result", "tool_use_id": call.id}
        
        try:
            result = await tool_dict[call.name].execute(**call.input)
            response["content"] = str(result)
        except KeyError:
            response["content"] = f"Tool '{call.name}' not found"
            response["is_error"] = True
        except Exception as e:
            response["content"] = f"Error executing tool: {str(e)}"
            response["is_error"] = True
        
        return response
    
    if parallel:
        return await asyncio.gather(
            *[_execute_single_tool(call) for call in tool_calls]
        )
    else:
        return [
            await _execute_single_tool(call) for call in tool_calls
        ]


class WebSearchAgent:
    """Claude-powered agent with enhanced web search capabilities using Brave Search and Firecrawl."""
    
    def __init__(
        self,
        name: str = "WebSearchAgent",
        system: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        config: Optional[ModelConfig] = None,
        verbose: bool = False,
        client: Optional[Anthropic] = None,
        message_params: Optional[dict[str, Any]] = None,
    ):
        """Initialize a WebSearchAgent.
        
        Args:
            name: Agent identifier for logging
            system: System prompt for the agent
            tools: List of tools available to the agent
            config: Model configuration with defaults
            verbose: Enable detailed logging
            client: Anthropic client instance
            message_params: Additional parameters for client.messages.create()
        """
        self.name = name
        self.system = system or self._default_system_prompt()
        self.verbose = verbose
        self.tools = list(tools or [BraveSearchTool(), FirecrawlContentTool()])
        self.config = config or ModelConfig()
        self.message_params = message_params or {}
        self.client = client or Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "")
        )
        self.history = MessageHistory(
            model=self.config.model,
            system=self.system,
            context_window_tokens=self.config.context_window_tokens,
            client=self.client,
        )
        
        if self.verbose:
            print(f"\n[{self.name}] Agent initialized with {len(self.tools)} tools")
            self._check_api_keys()
    
    def _check_api_keys(self):
        """Check if API keys are properly configured."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        
        print(f"🔑 API Key Status:")
        print(f"   Anthropic: {'✅' if anthropic_key else '❌'}")
        print(f"   Brave Search: {'✅' if brave_key else '❌ (fallback available)'}")
        print(f"   Firecrawl: {'✅' if firecrawl_key else '❌ (fallback available)'}")
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for enhanced web search agent."""
        return """You are an advanced AI research assistant with powerful web search and content extraction capabilities.

**Available Tools:**
🔍 **Brave Search**: High-quality web search with recent, relevant results
🔥 **Firecrawl**: Advanced content extraction that provides clean, readable text from web pages

**Search Strategy:**
1. Use targeted, specific search queries for better results
2. Search for recent information when dealing with current events
3. Extract detailed content from promising URLs for comprehensive analysis
4. Cross-reference multiple sources when possible
5. Always cite sources with URLs

**Best Practices:**
- Start with broad searches, then narrow down to specific topics
- Extract full content from key articles for detailed analysis
- Provide comprehensive answers with proper source attribution
- Mention if information might be outdated or if sources are limited
- Use follow-up searches to verify important claims

**Response Format:**
- Provide clear, well-structured answers
- Include relevant quotes from sources
- Always include source URLs for fact-checking
- Highlight any limitations or uncertainties in the information

You excel at finding current, accurate information and providing thorough, well-sourced responses."""
    
    def _prepare_message_params(self) -> dict[str, Any]:
        """Prepare parameters for client.messages.create() call."""
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self.system,
            "messages": self.history.format_for_api(),
            "tools": [tool.to_dict() for tool in self.tools],
            **self.message_params,
        }
    
    async def _agent_loop(self, user_input: str) -> Any:
        """Process user input and handle tool calls in a loop."""
        if self.verbose:
            print(f"\n[{self.name}] Received: {user_input}")
        await self.history.add_message("user", user_input, None)
        
        tool_dict = {tool.name: tool for tool in self.tools}
        
        while True:
            self.history.truncate()
            params = self._prepare_message_params()
            
            response = self.client.messages.create(**params)
            tool_calls = [
                block for block in response.content if block.type == "tool_use"
            ]
            
            if self.verbose:
                for block in response.content:
                    if block.type == "text":
                        print(f"\n[{self.name}] Output: {block.text}")
                    elif block.type == "tool_use":
                        params_str = ", ".join(
                            [f"{k}={v}" for k, v in block.input.items()]
                        )
                        print(
                            f"\n[{self.name}] Tool call: "
                            f"{block.name}({params_str})"
                        )
            
            await self.history.add_message(
                "assistant", response.content, response.usage
            )
            
            if tool_calls:
                tool_results = await execute_tools(
                    tool_calls,
                    tool_dict,
                )
                if self.verbose:
                    for block in tool_results:
                        content_preview = block.get('content', '')[:200] + "..." if len(block.get('content', '')) > 200 else block.get('content', '')
                        print(f"\n[{self.name}] Tool result: {content_preview}")
                await self.history.add_message("user", tool_results)
            else:
                return response
    
    async def run_async(self, user_input: str) -> Any:
        """Run agent asynchronously."""
        return await self._agent_loop(user_input)
    
    def run(self, user_input: str) -> Any:
        """Run agent synchronously."""
        return asyncio.run(self.run_async(user_input))
    
    def search_web(self, query: str, count: int = 5) -> str:
        """Convenience method for direct web search."""
        search_tool = BraveSearchTool()
        return asyncio.run(search_tool.execute(query, count))
    
    def extract_content(self, url: str, max_length: int = 8000) -> str:
        """Convenience method for content extraction."""
        content_tool = FirecrawlContentTool()
        return asyncio.run(content_tool.execute(url, max_length=max_length))


def main():
    """Example usage of the enhanced WebSearchAgent."""
    
    # Initialize the agent
    agent = WebSearchAgent(verbose=True)
    
    # Example queries showcasing enhanced capabilities
    queries = [
        "Virat Kohli's batting style",
    ]
    
    print("🔍 Enhanced Web Search Agent Demo")
    print("=" * 60)
    
    for query in queries:
        print(f"\n🤔 Query: {query}")
        print("-" * 40)
        
        try:
            response = agent.run(query)
            # Extract text content from response
            text_content = ""
            for block in response.content:
                if block.type == "text":
                    text_content += block.text
            
            print(f"🤖 Response: {text_content}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 60)


if __name__ == "__main__":
    main() 