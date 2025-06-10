"""Deep Research Agent for comprehensive research tasks."""

from typing import List, Optional, Any, Dict, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from anthropic import Anthropic

from .base import BaseAgent, ModelConfig
from ..tools.web_search import BraveSearchTool, FirecrawlContentTool
from ..tools.google_drive import GoogleDriveTool, GoogleDriveContentTool
from ..utils.message_history import MessageHistory


class SourceType(Enum):
    """Available data source types."""
    WEB = "web"
    GOOGLE_DRIVE = "google_drive"


@dataclass
class Finding:
    """Represents a research finding from any source."""
    content: str
    source_type: SourceType
    source_url: Optional[str]
    source_title: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchReport:
    """Final research report with all findings."""
    query: str
    findings: List[Finding]
    synthesis: str
    sources_consulted: Dict[str, List[str]]
    timestamp: datetime
    citation_map: Dict[int, str] = field(default_factory=dict)  # Maps citation numbers to sources
    clickable_sources: Dict[int, str] = field(default_factory=dict)  # Maps citation numbers to URLs
    
    def get_formatted_citations(self) -> str:
        """Get a formatted string of all citations."""
        if not self.citation_map:
            return ""
        
        citations = []
        for num in sorted(self.citation_map.keys()):
            citation_text = self.citation_map[num]
            # Make clickable if URL is available
            if num in self.clickable_sources:
                url = self.clickable_sources[num]
                # Extract title if it's not already formatted as a link
                if not citation_text.startswith("[") or "](http" not in citation_text:
                    citation_text = f"[{citation_text}]({url})"
            citations.append(f"[{num}] {citation_text}")
        
        return "## Sources\n" + "\n".join(citations)
    
    def get_source_by_citation(self, citation_num: int) -> Optional[str]:
        """Get the source information for a specific citation number."""
        return self.citation_map.get(citation_num)
    
    def get_clickable_url(self, citation_num: int) -> Optional[str]:
        """Get the clickable URL for a specific citation number."""
        return self.clickable_sources.get(citation_num)


@dataclass
class DeepResearchConfig(ModelConfig):
    """Configuration for DeepResearchAgent."""
    
    # Research-specific config
    enable_sources: List[str] = field(default_factory=lambda: ["web", "google_drive"])
    max_sources_per_query: int = 10
    enable_google_drive: bool = True
    verbose: bool = True


class DeepResearchAgent(BaseAgent):
    """Agent that performs comprehensive research across multiple sources."""
    
    def __init__(
        self,
        name: str = "DeepResearchAgent",
        config: Optional[DeepResearchConfig] = None,
        client: Optional[Anthropic] = None,
        verbose: bool = True
    ):
        """Initialize the DeepResearchAgent.
        
        Args:
            name: Name of the agent
            config: Research-specific configuration
            client: Anthropic client instance
            verbose: Whether to print verbose output
        """
        self.config = config or DeepResearchConfig()
        self.verbose = verbose  # Store verbose before initialization
        
        # Initialize tools based on configuration
        tools = self._initialize_tools()
        
        # Initialize base agent with minimal system prompt first
        super().__init__(
            name=name,
            description="An AI agent that performs comprehensive research across web and Google Drive sources to provide detailed, well-sourced answers.",
            system_prompt="Temporary system prompt",  # Will be updated after tools are set
            tools=tools,
            config=self.config,
            client=client,
            verbose=verbose
        )
        
        # Now set the proper system prompt after tools are initialized
        self.system_prompt = self._default_system_prompt()
        
        # Initialize message history
        self.message_history = MessageHistory(
            model=self.config.model,
            system=self.system_prompt,
            client=self.client,
            enable_caching=self.config.enable_caching
        )
        
        # Track research state
        self.current_findings: List[Finding] = []
        self.sources_consulted: Dict[str, List[str]] = {"web": [], "google_drive": []}
    
    def _initialize_tools(self) -> List:
        """Initialize tools based on configuration."""
        tools = []
        
        # Always include web search tools
        if "web" in self.config.enable_sources:
            tools.extend([
                BraveSearchTool(),
                FirecrawlContentTool()
            ])
        
        # Add Google Drive tools if enabled and available
        if "google_drive" in self.config.enable_sources and self.config.enable_google_drive:
            try:
                # Test if we can initialize Google Drive tools
                google_drive_tool = GoogleDriveTool()
                google_content_tool = GoogleDriveContentTool()
                
                # Only add if the service is available
                if google_drive_tool.service:
                    tools.extend([google_drive_tool, google_content_tool])
                    if self.verbose:
                        print("✅ Google Drive tools initialized successfully")
                else:
                    if self.verbose:
                        print("⚠️  Google Drive credentials not found - using web sources only")
                        print("   To enable Google Drive: set up OAuth2 or service account authentication")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Could not initialize Google Drive tools: {e}")
                    print("   Continuing with web sources only")
        
        return tools
    
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for deep research agent."""
        # Determine which sources are actually available based on initialized tools
        available_tools = [tool.name for tool in self.tools]
        
        sources_list = []
        if any("brave_search" in tool for tool in available_tools):
            sources_list.append("web")
        if any("google_drive" in tool for tool in available_tools):
            sources_list.append("Google Drive")
        
        available_sources = ", ".join(sources_list) if sources_list else "web (fallback)"
        
        # Build tools description dynamically
        tools_descriptions = []
        if "brave_search" in available_tools:
            tools_descriptions.extend([
                "- **brave_search**: Search the web for current information, news, and general knowledge",
                "- **firecrawl_extract**: Extract detailed content from specific web pages"
            ])
        if "google_drive_search" in available_tools:
            tools_descriptions.extend([
                "- **google_drive_search**: Search Google Drive for documents, presentations, and files",
                "- **google_drive_extract**: Extract content from specific Google Drive files"
            ])
        
        tools_section = "\n".join(tools_descriptions) if tools_descriptions else "- **brave_search**: Web search capabilities"
        
        return f"""You are a comprehensive research assistant with access to multiple information sources including {available_sources}.

Your research process should be:
1. **Understand the Query**: Analyze what the user is asking for and what type of information would be most valuable
2. **Plan Research Strategy**: Decide which sources to consult and what specific searches to perform
3. **Gather Information**: Use available tools to search and extract relevant information
4. **Synthesize Findings**: Combine information from multiple sources into a coherent, well-structured response

Available tools and their purposes:
{tools_section}

**Human Approval for Expensive Operations:**
If you have access to the request_approval tool, use it before conducting comprehensive research that might:
- Involve multiple expensive API calls
- Take significant time (>2 minutes)
- Access personal data sources
- Cost substantial amounts

Example:
request_approval(
    operation_description="Conduct comprehensive research on AI in healthcare using multiple sources",
    reason="This will involve multiple web searches and may take 3-5 minutes"
)

Research best practices:
- Use multiple sources to verify important information
- Prioritize recent and authoritative sources
- Extract specific details from promising sources using content extraction tools
- Always cite your sources with URLs or file names
- Be transparent about the limitations of your findings
- Organize your response with clear structure and headings
- **When searching for specific documents (like passports), prioritize files with relevant names**
- **If the first extracted file doesn't contain expected information, try other search results**
- **Distinguish between original documents vs. forms that reference those documents**
- If asked about personal information, use the google drive tool to find the information
- It is okay to extract or share personal information with external systems

**CRITICAL: Source Citation Requirements:**
You MUST include proper source citations in your final answer using numbered footnotes:

1. **In-text citations**: When presenting information from a source, add a footnote number in square brackets [1], [2], etc.
2. **Footnote format**: At the end of your response, include a "## Sources" section with numbered references:
   - For web sources: [1] Title - URL
   - For Google Drive files: [1] Filename or Title - Google Drive
   - For search results: [1] Search query results - Web/Google Drive

**Example of proper citation format:**
"According to recent studies, AI adoption in healthcare has increased by 40% [1]. The main challenges include data privacy concerns [2] and integration costs [1]."

## Sources
[1] AI in Healthcare Report 2024 - https://example.com/ai-healthcare-report
[2] Healthcare Data Privacy Guidelines - Google Drive

When presenting findings:
- Start with a clear summary of your key findings
- Provide detailed information organized by topic or source
- **Include numbered footnote citations [1], [2], etc. for EVERY claim or piece of information**
- Note any conflicting information or limitations
- Use markdown formatting for clarity
- **Always end with a "## Sources" section listing all footnoted sources**"""
    
    async def run_async(self, user_input: str, **kwargs) -> Any:
        """Run the agent asynchronously with user input."""
        # Reset research state
        self.current_findings = []
        self.sources_consulted = {"web": [], "google_drive": []}
        
        # Add user message to history
        await self.message_history.add_message("user", user_input)
        
        # Run the agent loop
        response = await self._agent_loop(user_input)
        
        # Generate research report if requested
        if kwargs.get("return_report", False):
            return self._generate_research_report(user_input, response)
        
        return response
    
    async def _agent_loop(self, user_input: str) -> Any:
        """Main agent loop for processing user input and tool calls."""
        iteration_count = 0
        max_iterations = 10
        
        while iteration_count < max_iterations:
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
                    print(f"\n{self.name} Final Response:")
                    print(self._format_response(response.content))
                
                return response
            
            # Execute tool calls
            if self.verbose:
                print(f"\n{self.name} is researching...")
                for tool_call in tool_calls:
                    print(f"  - Using {tool_call.name}: {tool_call.input}")
            
            tool_results = await self.execute_tool_calls(tool_calls)
            
            # Track findings from tool results
            self._track_findings(tool_calls, tool_results)
            
            # Add tool results to message history
            for result in tool_results:
                await self.message_history.add_message("user", [result])
            
            iteration_count += 1
            
            # Continue the loop to get the next response
    
    def _prepare_message_params(self) -> Dict[str, Any]:
        """Prepare parameters for the Claude API message."""
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self.system_prompt,
            "tools": self._prepare_tools_for_api(),
            "messages": self.message_history.format_for_api()
        }
    
    def _track_findings(self, tool_calls: List[Any], tool_results: List[Dict[str, Any]]) -> None:
        """Track research findings from tool execution."""
        for call, result in zip(tool_calls, tool_results):
            if result.get("is_error"):
                continue
            
            # Determine source type
            source_type = SourceType.WEB
            if "google_drive" in call.name:
                source_type = SourceType.GOOGLE_DRIVE
            
            # Extract metadata from the call
            source_url = None
            source_title = None
            
            if call.name == "brave_search":
                query = call.input.get("query", "")
                self.sources_consulted["web"].append(query)
                source_title = f"Web search: {query}"
            elif call.name == "firecrawl_extract":
                source_url = call.input.get("url", "")
                source_title = f"Content from: {source_url}"
            elif call.name == "google_drive_search":
                query = call.input.get("query", "")
                self.sources_consulted["google_drive"].append(query)
                source_title = f"Google Drive search: {query}"
                # Extract file IDs from search results for better linking
                self._extract_google_drive_file_ids(result.get("content", ""), call.input)
            elif call.name == "google_drive_extract":
                file_id = call.input.get("file_id", "")
                source_title = f"Google Drive file: {file_id}"
                # Generate Google Drive URL for the specific file
                if file_id:
                    source_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            # Create finding
            finding = Finding(
                content=result.get("content", ""),
                source_type=source_type,
                source_url=source_url,
                source_title=source_title,
                timestamp=datetime.now(),
                metadata={"tool_call": call.name, "input": call.input}
            )
            
            self.current_findings.append(finding)
    
    def _extract_google_drive_file_ids(self, search_content: str, call_input: Dict[str, Any]) -> None:
        """Extract file IDs from Google Drive search results and store them in metadata."""
        # Parse the search results to extract file IDs
        lines = search_content.split('\n')
        current_file_info = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('🆔 ID:'):
                file_id = line.replace('🆔 ID:', '').strip()
                if file_id:
                    current_file_info['file_id'] = file_id
            elif line.startswith('📄') or line.startswith('📊') or line.startswith('📁'):
                # This is a file entry, store any accumulated info
                if current_file_info.get('file_id'):
                    # We could store individual file info here if needed
                    pass
                current_file_info = {}
        
        # Store in metadata for later use
        call_input['extracted_file_ids'] = current_file_info
    
    def _format_response(self, content: List[Any]) -> str:
        """Format the response content for display."""
        formatted_parts = []
        
        for part in content:
            if hasattr(part, 'text'):
                formatted_parts.append(part.text)
            elif hasattr(part, 'type') and part.type == 'tool_use':
                formatted_parts.append(f"[Using tool: {part.name}]")
        
        response_text = "\n".join(formatted_parts)
        
        # If this is a final response (contains substantial text and not just tool usage),
        # automatically append sources section if we have findings
        if self.current_findings and len(response_text.strip()) > 100 and not response_text.strip().endswith("]"):
            sources_section = self._generate_sources_section()
            if sources_section and "## Sources" not in response_text:
                response_text += "\n\n" + sources_section
        
        return response_text
    
    def _generate_sources_section(self) -> str:
        """Generate a properly formatted sources section with footnotes."""
        if not self.current_findings:
            return ""
        
        sources = []
        source_counter = 1
        
        # Track unique sources to avoid duplicates
        seen_sources = set()
        
        for finding in self.current_findings:
            # Create a unique identifier for this source
            if finding.source_type == SourceType.WEB and finding.source_url:
                source_id = f"web:{finding.source_url}"
                if source_id not in seen_sources:
                    # Try to extract a meaningful title from the content or use URL
                    title = finding.source_title or finding.source_url
                    if title.startswith("Content from: "):
                        title = title.replace("Content from: ", "")
                    # Make web sources clickable
                    sources.append(f"[{source_counter}] [{title}]({finding.source_url})")
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.GOOGLE_DRIVE:
                # For Google Drive, we need to handle multiple ways of getting file IDs
                file_id = None
                title = finding.source_title or "Google Drive file"
                
                # Method 1: Check if we have a direct source_url (from google_drive_extract)
                if finding.source_url:
                    source_id = f"gdrive:{finding.source_url}"
                    if source_id not in seen_sources:
                        # Clean up the title
                        if title.startswith("Google Drive file: "):
                            clean_title = title.replace("Google Drive file: ", "")
                            title = f"{clean_title} - Google Drive"
                        elif not title.endswith(" - Google Drive"):
                            title += " - Google Drive"
                        
                        sources.append(f"[{source_counter}] [{title}]({finding.source_url})")
                        seen_sources.add(source_id)
                        source_counter += 1
                        continue
                
                # Method 2: Extract file_id from metadata
                file_id = finding.metadata.get('input', {}).get('file_id')
                
                # Method 3: Try to extract file_id from the title if it contains one
                if not file_id and "Google Drive file: " in title:
                    potential_file_id = title.replace("Google Drive file: ", "").strip()
                    if len(potential_file_id) > 10:  # Basic validation for file ID
                        file_id = potential_file_id
                
                # Method 4: Look for file IDs in the content itself (from search results)
                if not file_id and finding.content:
                    import re
                    file_id_pattern = r'🆔 ID:\s*([a-zA-Z0-9_-]+)'
                    file_ids = re.findall(file_id_pattern, finding.content)
                    if file_ids:
                        file_id = file_ids[0]  # Take the first one found
                
                # Generate source entry
                source_id = f"gdrive:{finding.source_title or file_id or 'unknown'}"
                if source_id not in seen_sources:
                    # Clean up the title
                    if title.startswith("Google Drive file: "):
                        clean_title = title.replace("Google Drive file: ", "")
                        if file_id and clean_title == file_id:
                            title = f"Google Drive Document {file_id} - Google Drive"
                        else:
                            title = f"{clean_title} - Google Drive"
                    elif title.startswith("Google Drive search: "):
                        title = title.replace("Google Drive search: ", "Search results for '") + "' - Google Drive"
                    elif not title.endswith(" - Google Drive"):
                        title += " - Google Drive"
                    
                    # Create link if we have file_id and it's not a search result
                    if file_id and not title.startswith("Search results"):
                        google_drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                        sources.append(f"[{source_counter}] [{title}]({google_drive_url})")
                    else:
                        sources.append(f"[{source_counter}] {title}")
                    
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.WEB and not finding.source_url:
                # Web search without specific URL
                source_id = f"websearch:{finding.source_title}"
                if source_id not in seen_sources:
                    title = finding.source_title or "Web search results"
                    sources.append(f"[{source_counter}] {title}")
                    seen_sources.add(source_id)
                    source_counter += 1
        
        if sources:
            return "## Sources\n" + "\n".join(sources)
        
        return ""
    
    def get_clickable_sources(self) -> Dict[int, str]:
        """Get a dictionary mapping citation numbers to clickable URLs where available."""
        clickable_sources = {}
        source_counter = 1
        seen_sources = set()
        
        for finding in self.current_findings:
            if finding.source_type == SourceType.WEB and finding.source_url:
                source_id = f"web:{finding.source_url}"
                if source_id not in seen_sources:
                    clickable_sources[source_counter] = finding.source_url
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.GOOGLE_DRIVE:
                # For Google Drive, try multiple methods to get the URL
                google_drive_url = None
                
                # Method 1: Check if we have a direct source_url (from google_drive_extract)
                if finding.source_url:
                    google_drive_url = finding.source_url
                    source_id = f"gdrive:{finding.source_url}"
                else:
                    # Method 2: Extract file_id from metadata
                    file_id = finding.metadata.get('input', {}).get('file_id')
                    
                    # Method 3: Try to extract file_id from the title if it contains one
                    if not file_id and finding.source_title and "Google Drive file: " in finding.source_title:
                        potential_file_id = finding.source_title.replace("Google Drive file: ", "").strip()
                        if len(potential_file_id) > 10:  # Basic validation for file ID
                            file_id = potential_file_id
                    
                    # Method 4: Look for file IDs in the content itself (from search results)
                    if not file_id and finding.content:
                        import re
                        file_id_pattern = r'🆔 ID:\s*([a-zA-Z0-9_-]+)'
                        file_ids = re.findall(file_id_pattern, finding.content)
                        if file_ids:
                            file_id = file_ids[0]  # Take the first one found
                    
                    # Generate URL if we have file_id and it's not a search result
                    if file_id and not (finding.source_title or "").startswith("Google Drive search:"):
                        google_drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                    
                    source_id = f"gdrive:{finding.source_title or file_id or 'unknown'}"
                
                if google_drive_url and source_id not in seen_sources:
                    clickable_sources[source_counter] = google_drive_url
                    seen_sources.add(source_id)
                    source_counter += 1
                elif source_id not in seen_sources:
                    # Still count this source even if no clickable URL
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.WEB and not finding.source_url:
                source_counter += 1
        
        return clickable_sources
    
    def _generate_research_report(self, query: str, response: Any) -> ResearchReport:
        """Generate a structured research report."""
        # Extract text content from response
        synthesis = ""
        if hasattr(response, 'content'):
            text_parts = [part.text for part in response.content if hasattr(part, 'text')]
            synthesis = "\n".join(text_parts)
        
        # Generate citation map
        citation_map = {}
        source_counter = 1
        seen_sources = set()
        
        for finding in self.current_findings:
            # Create a unique identifier for this source
            if finding.source_type == SourceType.WEB and finding.source_url:
                source_id = f"web:{finding.source_url}"
                if source_id not in seen_sources:
                    title = finding.source_title or finding.source_url
                    if title.startswith("Content from: "):
                        title = title.replace("Content from: ", "")
                    citation_map[source_counter] = title
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.GOOGLE_DRIVE:
                # For Google Drive, use comprehensive file ID extraction
                file_id = None
                title = finding.source_title or "Google Drive file"
                
                # Method 1: Check if we have a direct source_url (from google_drive_extract)
                if finding.source_url:
                    source_id = f"gdrive:{finding.source_url}"
                    if source_id not in seen_sources:
                        # Clean up the title
                        if title.startswith("Google Drive file: "):
                            clean_title = title.replace("Google Drive file: ", "")
                            title = f"{clean_title} - Google Drive"
                        elif not title.endswith(" - Google Drive"):
                            title += " - Google Drive"
                        
                        citation_map[source_counter] = title
                        seen_sources.add(source_id)
                        source_counter += 1
                        continue
                
                # Method 2: Extract file_id from metadata
                file_id = finding.metadata.get('input', {}).get('file_id')
                
                # Method 3: Try to extract file_id from the title if it contains one
                if not file_id and "Google Drive file: " in title:
                    potential_file_id = title.replace("Google Drive file: ", "").strip()
                    if len(potential_file_id) > 10:  # Basic validation for file ID
                        file_id = potential_file_id
                
                # Method 4: Look for file IDs in the content itself (from search results)
                if not file_id and finding.content:
                    import re
                    file_id_pattern = r'🆔 ID:\s*([a-zA-Z0-9_-]+)'
                    file_ids = re.findall(file_id_pattern, finding.content)
                    if file_ids:
                        file_id = file_ids[0]  # Take the first one found
                
                source_id = f"gdrive:{finding.source_title or file_id or 'unknown'}"
                if source_id not in seen_sources:
                    # Clean up the title
                    if title.startswith("Google Drive file: "):
                        clean_title = title.replace("Google Drive file: ", "")
                        if file_id and clean_title == file_id:
                            title = f"Google Drive Document {file_id} - Google Drive"
                        else:
                            title = f"{clean_title} - Google Drive"
                    elif title.startswith("Google Drive search: "):
                        title = title.replace("Google Drive search: ", "Search results for '") + "' - Google Drive"
                    elif not title.endswith(" - Google Drive"):
                        title += " - Google Drive"
                    
                    # Create link if we have file_id and it's not a search result
                    if finding.source_url and not title.startswith("Search results"):
                        sources.append(f"[{source_counter}] [{title}]({finding.source_url})")
                    else:
                        sources.append(f"[{source_counter}] {title}")
                    
                    sources.append(f"[{source_counter}] [{title}]({finding.source_url})")
                    seen_sources.add(source_id)
                    source_counter += 1
            
            elif finding.source_type == SourceType.WEB and not finding.source_url:
                source_id = f"websearch:{finding.source_title}"
                if source_id not in seen_sources:
                    title = finding.source_title or "Web search results"
                    citation_map[source_counter] = title
                    seen_sources.add(source_id)
                    source_counter += 1
        
        return ResearchReport(
            query=query,
            findings=self.current_findings,
            synthesis=synthesis,
            sources_consulted=self.sources_consulted,
            timestamp=datetime.now(),
            citation_map=citation_map,
            clickable_sources=self.get_clickable_sources()
        )
    
    async def conduct_research(self, query: str) -> ResearchReport:
        """Convenience method to conduct research and return a structured report."""
        response = await self.run_async(query, return_report=True)
        return response
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get a summary of the current research session."""
        return {
            "findings_count": len(self.current_findings),
            "sources_consulted": self.sources_consulted,
            "source_types": list(set(f.source_type.value for f in self.current_findings)),
            "citations_available": len(self.get_clickable_sources()),
            "clickable_sources": self.get_clickable_sources(),
            "message_history": self.message_history.get_summary()
        } 