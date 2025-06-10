"""Web search tools for agents."""

import os
import requests
from typing import List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from firecrawl import FirecrawlApp

from .base import Tool


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
            
            params = {
                "q": query,
                "count": min(count, 20),
                "country": country,
                "search_lang": "en"
            }
            
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
            # Configure scraping options
            scrape_options = {
                "formats": formats,
                "includeTags": include_tags,
                "excludeTags": exclude_tags,
                "waitFor": 2000,  # Wait 2 seconds for dynamic content
                "timeout": 30000   # 30 second timeout
            }
            
            # Scrape the URL
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