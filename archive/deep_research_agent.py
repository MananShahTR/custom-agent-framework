"""Deep Research Agent with ReAct framework for intelligent multi-source research."""

import asyncio
import os
import json
import re
import base64
import io
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime
from enum import Enum

from anthropic import Anthropic
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Import base components from web_search_agent
from web_search_agent import (
    Tool, BraveSearchTool, FirecrawlContentTool, 
    MessageHistory, ModelConfig, execute_tools
)

# Load environment variables
load_dotenv()


class SourceType(Enum):
    """Available data source types."""
    WEB = "web"
    GOOGLE_DRIVE = "google_drive"
    GMAIL = "gmail"  # For future implementation
    DATABASE = "database"  # For future implementation


@dataclass
class Finding:
    """Represents a research finding from any source."""
    content: str
    source_type: SourceType
    source_url: Optional[str]
    source_title: Optional[str]
    timestamp: datetime
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThoughtProcess:
    """Represents the reasoning output from ReAct thinking step."""
    analysis: str
    identified_gaps: List[str]
    recommended_sources: Dict[str, str]  # source -> reason
    recommended_queries: Dict[str, List[str]]  # source -> queries
    confidence_assessment: float


@dataclass
class Reflection:
    """Represents the reflection on action results."""
    quality_assessment: str
    new_insights: List[str]
    remaining_questions: List[str]
    suggested_pivots: List[str]
    confidence_update: float
    should_continue: bool


@dataclass
class ResearchState:
    """Tracks the current state of research."""
    query: str
    objective: str
    current_findings: List[Finding]
    sources_consulted: Dict[str, List[str]]  # source_type -> [queries]
    confidence_level: float
    gaps_identified: List[str]
    next_steps: List[str]
    iteration_count: int
    max_iterations: int = 10
    
    def should_continue(self) -> bool:
        """Determine if research should continue."""
        return (
            self.confidence_level < 0.8 and 
            self.iteration_count < self.max_iterations and
            len(self.next_steps) > 0
        )


@dataclass
class ResearchReport:
    """Final research report with all findings."""
    query: str
    objective: str
    findings: List[Finding]
    synthesis: str
    confidence_level: float
    sources_consulted: Dict[str, List[str]]
    iterations_performed: int
    timestamp: datetime


class GoogleDriveTool(Tool):
    """Tool for searching and retrieving content from Google Drive."""
    
    def __init__(self):
        super().__init__(
            name="google_drive_search",
            description="Search and retrieve documents from Google Drive. Can search by filename, content, or metadata.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Google Drive. Supports Drive search syntax."
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by file types (e.g., ['document', 'spreadsheet', 'pdf'])",
                        "default": []
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Sort order for results",
                        "enum": ["modifiedTime", "name", "createdTime"],
                        "default": "modifiedTime"
                    }
                },
                "required": ["query"]
            }
        )
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive API service."""
        creds = None
        
        # Try multiple authentication methods
        # Method 1: OAuth2 token (for user authentication)
        token_path = 'token.pickle'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Method 2: Service account (for server applications)
        if not creds:
            service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            if service_account_file and os.path.exists(service_account_file):
                creds = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
        
        # Method 3: Application default credentials
        if not creds:
            try:
                from google.auth import default
                creds, _ = default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
            except Exception:
                pass
        
        if not creds:
            print("⚠️  Warning: Google Drive credentials not found. Please set up authentication.")
            return None
        
        try:
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Google Drive service: {str(e)}")
            return None
    
    async def execute(
        self, 
        query: str, 
        file_types: List[str] = None,
        max_results: int = 2,
        order_by: str = "modifiedTime"
    ) -> str:
        """Search Google Drive and return formatted results."""
        if not self.service:
            return "❌ Google Drive service not initialized. Please check authentication."
        
        try:
            # Build the search query
            search_query = self._build_search_query(query, file_types)
            
            # Execute search
            results = self.service.files().list(
                q=search_query,
                pageSize=max_results,
                orderBy=f"{order_by} desc",
                fields="files(id, name, mimeType, modifiedTime, webViewLink, size, description)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return f"📁 No files found in Google Drive matching: {query}"
            
            # Format results
            formatted_results = f"📁 **Google Drive Search Results for:** {query}\n\n"
            
            for i, file in enumerate(files, 1):
                file_type = self._get_file_type_emoji(file['mimeType'])
                formatted_results += f"{i}. {file_type} **{file['name']}**\n"
                
                if file.get('description'):
                    formatted_results += f"   📝 {file['description']}\n"
                
                formatted_results += f"   📅 Modified: {file['modifiedTime'][:10]}\n"
                
                if file.get('size'):
                    size_mb = int(file['size']) / (1024 * 1024)
                    formatted_results += f"   📊 Size: {size_mb:.1f} MB\n"
                
                formatted_results += f"   🔗 Link: {file.get('webViewLink', 'N/A')}\n"
                formatted_results += f"   🆔 ID: {file['id']}\n\n"
            
            return formatted_results
            
        except HttpError as e:
            return f"❌ Google Drive API error: {str(e)}"
        except Exception as e:
            return f"❌ Error searching Google Drive: {str(e)}"
    
    def _build_search_query(self, query: str, file_types: List[str] = None) -> str:
        """Build Google Drive API search query."""
        # Start with the user query
        search_parts = [f"fullText contains '{query}'"]
        
        # Add file type filters if specified
        if file_types:
            mime_types = []
            for file_type in file_types:
                if file_type.lower() == 'document':
                    mime_types.append("mimeType='application/vnd.google-apps.document'")
                elif file_type.lower() == 'spreadsheet':
                    mime_types.append("mimeType='application/vnd.google-apps.spreadsheet'")
                elif file_type.lower() == 'presentation':
                    mime_types.append("mimeType='application/vnd.google-apps.presentation'")
                elif file_type.lower() == 'pdf':
                    mime_types.append("mimeType='application/pdf'")
                elif file_type.lower() == 'folder':
                    mime_types.append("mimeType='application/vnd.google-apps.folder'")
            
            if mime_types:
                search_parts.append(f"({' or '.join(mime_types)})")
        
        # Exclude trashed files
        search_parts.append("trashed=false")
        
        return " and ".join(search_parts)
    
    def _get_file_type_emoji(self, mime_type: str) -> str:
        """Get emoji representation for file type."""
        emoji_map = {
            'application/vnd.google-apps.document': '📄',
            'application/vnd.google-apps.spreadsheet': '📊',
            'application/vnd.google-apps.presentation': '📊',
            'application/pdf': '📕',
            'application/vnd.google-apps.folder': '📁',
            'image/': '🖼️',
            'video/': '🎥',
            'audio/': '🎵'
        }
        
        for key, emoji in emoji_map.items():
            if key in mime_type:
                return emoji
        return '📎'


class GoogleDriveContentTool(Tool):
    """Tool for extracting content from Google Drive files."""
    
    def __init__(self, client: Optional[Anthropic] = None):
        super().__init__(
            name="google_drive_extract",
            description="Extract and read content from Google Drive files by file ID.",
            input_schema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID to extract content from"
                    },
                    "export_format": {
                        "type": "string",
                        "description": "Export format for Google Docs files",
                        "enum": ["text/plain", "text/html", "application/pdf"],
                        "default": "text/plain"
                    }
                },
                "required": ["file_id"]
            }
        )
        self.service = self._initialize_service()
        self.client = client or Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    
    def _initialize_service(self):
        """Initialize Google Drive API service (same as GoogleDriveTool)."""
        # Reuse the same initialization logic
        return GoogleDriveTool()._initialize_service()
    
    async def execute(self, file_id: str, export_format: str = "text/plain") -> str:
        """Extract content from a Google Drive file."""
        if not self.service:
            return "❌ Google Drive service not initialized. Please check authentication."
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="name, mimeType, size, modifiedTime"
            ).execute()
            
            file_name = file_metadata.get('name', 'Unknown')
            mime_type = file_metadata.get('mimeType', '')
            
            # Extract content based on file type
            content = ""
            
            if 'google-apps' in mime_type:
                # Export Google Docs/Sheets/Slides
                content = self._export_google_file(file_id, mime_type, export_format)
            else:
                # Download regular files
                content = self._download_file_content(file_id, mime_type)
            
            if not content:
                return f"❌ Could not extract content from file: {file_name}"
            
            # Format response
            response = f"📄 **Google Drive Content Extraction**\n"
            response += f"📋 **File:** {file_name}\n"
            response += f"📅 **Modified:** {file_metadata.get('modifiedTime', 'Unknown')[:10]}\n"
            response += f"\n---\n\n"
            response += content
            
            return response
            
        except HttpError as e:
            return f"❌ Google Drive API error: {str(e)}"
        except Exception as e:
            return f"❌ Error extracting content: {str(e)}"
    
    def _export_google_file(self, file_id: str, mime_type: str, export_format: str) -> str:
        """Export Google Docs/Sheets/Slides to text."""
        try:
            # Determine export MIME type
            if 'document' in mime_type:
                export_mime = export_format
            elif 'spreadsheet' in mime_type:
                export_mime = 'text/csv'
            elif 'presentation' in mime_type:
                export_mime = 'text/plain'
            else:
                export_mime = 'text/plain'
            
            # Export the file
            response = self.service.files().export(
                fileId=file_id,
                mimeType=export_mime
            ).execute()
            
            # Decode content
            if isinstance(response, bytes):
                content = response.decode('utf-8', errors='ignore')
            else:
                content = str(response)
            
            # Truncate if too long
            max_length = 8000
            if len(content) > max_length:
                content = content[:max_length] + "\n\n... (content truncated)"
            
            return content
            
        except Exception as e:
            return f"Error exporting file: {str(e)}"
    
    def _download_file_content(self, file_id: str, mime_type: str) -> str:
        """Download and extract content from regular files using Anthropic."""
        try:
            # Download the file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            
            # Download the file
            downloader = request.execute()
            
            # For binary content, we need to handle it differently
            if isinstance(downloader, bytes):
                file_content.write(downloader)
            else:
                # Try alternative download method
                try:
                    import googleapiclient.http
                    downloader = googleapiclient.http.MediaIoBaseDownload(file_content, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                except Exception:
                    # Fallback to direct HTTP request
                    response = request.http.request(request.uri)
                    if response[0].status != 200:
                        return f"Error downloading file: HTTP {response[0].status}"
                    file_content.write(response[1])
            
            file_content.seek(0)
            
            # Determine file type and processing method
            if mime_type.startswith('image/'):
                return self._extract_image_content(file_content.getvalue(), mime_type)
            elif mime_type == 'application/pdf':
                return self._extract_pdf_content(file_content.getvalue())
            elif mime_type.startswith('text/'):
                # Text files can be read directly
                try:
                    text_content = file_content.getvalue().decode('utf-8', errors='ignore')
                    max_length = 8000
                    if len(text_content) > max_length:
                        text_content = text_content[:max_length] + "\n\n... (content truncated)"
                    return text_content
                except Exception as e:
                    return f"Error decoding text file: {str(e)}"
            elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return self._extract_document_content(file_content.getvalue(), mime_type)
            else:
                # For other file types, try to extract with Anthropic
                return self._extract_with_anthropic(file_content.getvalue(), mime_type)
                
        except Exception as e:
            return f"Error downloading file: {str(e)}"
    
    def _extract_image_content(self, file_bytes: bytes, mime_type: str) -> str:
        """Extract content from images using Anthropic's vision capabilities."""
        try:
            # Convert to base64
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            # Determine media type
            media_type = mime_type if mime_type else "image/jpeg"
            
            # Send to Anthropic
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please describe what you see in this image. If there's any text, transcribe it completely. If it appears to be a document, extract all the information you can see."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            return f"🖼️ Image Content:\n\n{response.content[0].text}"
            
        except Exception as e:
            return f"Error extracting image content: {str(e)}"
    
    def _extract_pdf_content(self, file_bytes: bytes) -> str:
        """Extract content from PDFs using Anthropic."""
        try:
            # For PDFs, we'll send it as a document to Anthropic
            # Note: This requires the PDF to be relatively small
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            
            # Check file size (Anthropic has limits)
            size_mb = len(file_bytes) / (1024 * 1024)
            if size_mb > 10:  # 10MB limit for safety
                return f"📕 PDF file too large ({size_mb:.1f} MB). Maximum supported size is 10 MB."
            
            # Send to Anthropic as a document
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract and summarize all the text content from this PDF document. Include all important information, data, and key points."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": base64_pdf
                                }
                            }
                        ]
                    }
                ]
            )
            
            return f"📕 PDF Content:\n\n{response.content[0].text}"
            
        except Exception as e:
            # If document type fails, try as image (for scanned PDFs)
            if "document" in str(e).lower():
                return self._extract_pdf_as_images(file_bytes)
            return f"Error extracting PDF content: {str(e)}"
    
    def _extract_pdf_as_images(self, file_bytes: bytes) -> str:
        """Fallback: Extract PDF content by treating it as images."""
        # This is a simplified version - in production you'd use a PDF library
        # to extract individual pages as images
        return "📕 PDF appears to be scanned. Full image extraction from PDFs requires additional libraries (e.g., pdf2image)."
    
    def _extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        """Extract content from Word documents using Anthropic."""
        try:
            base64_doc = base64.b64encode(file_bytes).decode('utf-8')
            
            # Check file size
            size_mb = len(file_bytes) / (1024 * 1024)
            if size_mb > 10:
                return f"📄 Document file too large ({size_mb:.1f} MB). Maximum supported size is 10 MB."
            
            # Send to Anthropic
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all the text content from this document. Include all sections, headings, and important information."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": base64_doc
                                }
                            }
                        ]
                    }
                ]
            )
            
            return f"📄 Document Content:\n\n{response.content[0].text}"
            
        except Exception as e:
            return f"Error extracting document content: {str(e)}"
    
    def _extract_with_anthropic(self, file_bytes: bytes, mime_type: str) -> str:
        """Generic extraction using Anthropic for unknown file types."""
        try:
            # Try to send as a generic document
            base64_file = base64.b64encode(file_bytes).decode('utf-8')
            
            size_mb = len(file_bytes) / (1024 * 1024)
            if size_mb > 10:
                return f"📎 File too large ({size_mb:.1f} MB). Maximum supported size is 10 MB."
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Please analyze this file (type: {mime_type}) and extract any readable content or describe what it contains."
                            },
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type if mime_type else "application/octet-stream",
                                    "data": base64_file
                                }
                            }
                        ]
                    }
                ]
            )
            
            return f"📎 File Content:\n\n{response.content[0].text}"
            
        except Exception as e:
            return f"📎 Unable to extract content from this file type ({mime_type}): {str(e)}"


class ReActReasoningEngine:
    """Implements ReAct framework for research decisions."""
    
    def __init__(self, client: Anthropic, model: str = "claude-3-sonnet-20240229"):
        self.client = client
        self.model = model
        self.reasoning_system_prompt = self._get_reasoning_prompt()
        self.reflection_system_prompt = self._get_reflection_prompt()
    
    def _get_reasoning_prompt(self) -> str:
        """Get the system prompt for reasoning."""
        return """You are a research orchestrator using the ReAct framework. Your role is to:

1. **Analyze** the current research state and identify what information is still needed
2. **Reason** about which data sources would be most valuable to consult next
3. **Plan** specific queries for each data source
4. **Assess** confidence in current findings

For each reasoning step, consider:
- What do we know so far?
- What are the gaps in our knowledge?
- Which sources haven't been consulted yet?
- Would cross-referencing sources provide validation?
- Are there contradictions that need resolution?

Available sources:
- **web**: Best for current events, public information, broad coverage
- **google_drive**: Best for internal documents, reports, structured data

Output your reasoning in JSON format:
{
    "analysis": "Current understanding of the research state",
    "identified_gaps": ["gap1", "gap2"],
    "recommended_sources": {
        "source_name": "reason for using this source"
    },
    "recommended_queries": {
        "source_name": ["query1", "query2"]
    },
    "confidence_assessment": 0.0 to 1.0
}"""
    
    def _get_reflection_prompt(self) -> str:
        """Get the system prompt for reflection."""
        return """You are evaluating research results using the ReAct framework. Your role is to:

1. **Assess** the quality and relevance of new information
2. **Integrate** new findings with existing knowledge
3. **Identify** contradictions or confirmations
4. **Determine** if the research objective is met
5. **Recommend** next steps if needed

For each reflection, consider:
- Does this information answer our questions?
- How reliable are these sources?
- Are there contradictions with previous findings?
- What new questions does this raise?
- Should we pivot our research approach?

Output your reflection in JSON format:
{
    "quality_assessment": "high/medium/low with reasons",
    "new_insights": ["insight1", "insight2"],
    "remaining_questions": ["question1", "question2"],
    "suggested_pivots": ["pivot1", "pivot2"],
    "confidence_update": 0.0 to 1.0,
    "should_continue": true/false
}"""
    
    async def think(
        self, 
        state: ResearchState,
        available_sources: List[str]
    ) -> ThoughtProcess:
        """Generate reasoning about next research steps."""
        
        # Build context for reasoning
        context = f"""
Current Research State:
- Query: {state.query}
- Objective: {state.objective}
- Findings so far: {len(state.current_findings)} items
- Sources consulted: {json.dumps(state.sources_consulted)}
- Current confidence: {state.confidence_level}
- Identified gaps: {json.dumps(state.gaps_identified)}
- Iteration: {state.iteration_count + 1}/{state.max_iterations}

Available sources: {json.dumps(available_sources)}

Recent findings summary:
"""
        # Add summaries of recent findings
        for finding in state.current_findings[-5:]:  # Last 5 findings
            context += f"- [{finding.source_type.value}] {finding.content[:200]}...\n"
        
        # Call LLM for reasoning
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            system=self.reasoning_system_prompt,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        
        # Parse response
        try:
            reasoning_text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', reasoning_text, re.DOTALL)
            if json_match:
                reasoning_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                reasoning_data = {
                    "analysis": reasoning_text,
                    "identified_gaps": [],
                    "recommended_sources": {"web": "general search"},
                    "recommended_queries": {"web": [state.query]},
                    "confidence_assessment": state.confidence_level
                }
            
            return ThoughtProcess(
                analysis=reasoning_data.get("analysis", ""),
                identified_gaps=reasoning_data.get("identified_gaps", []),
                recommended_sources=reasoning_data.get("recommended_sources", {}),
                recommended_queries=reasoning_data.get("recommended_queries", {}),
                confidence_assessment=reasoning_data.get("confidence_assessment", 0.5)
            )
            
        except Exception as e:
            print(f"Error parsing reasoning response: {e}")
            # Return default reasoning
            return ThoughtProcess(
                analysis="Need to search for more information",
                identified_gaps=[],
                recommended_sources={"web": "general search"},
                recommended_queries={"web": [state.query]},
                confidence_assessment=state.confidence_level
            )
    
    async def reflect(
        self,
        state: ResearchState,
        new_findings: List[Finding]
    ) -> Reflection:
        """Reflect on action results and update strategy."""
        
        # Build context for reflection
        context = f"""
Research Objective: {state.objective}
Current confidence level: {state.confidence_level}
Iteration: {state.iteration_count}/{state.max_iterations}

New findings from this iteration:
"""
        # Add new findings
        for finding in new_findings:
            context += f"\n[{finding.source_type.value}] {finding.source_title or 'Untitled'}\n"
            context += f"Content: {finding.content[:300]}...\n"
            context += f"Relevance: {finding.relevance_score}\n"
        
        context += f"\nTotal findings so far: {len(state.current_findings)}"
        
        # Call LLM for reflection
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            system=self.reflection_system_prompt,
            messages=[
                {"role": "user", "content": context}
            ]
        )
        
        # Parse response
        try:
            reflection_text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', reflection_text, re.DOTALL)
            if json_match:
                reflection_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                reflection_data = {
                    "quality_assessment": "medium",
                    "new_insights": [],
                    "remaining_questions": [],
                    "suggested_pivots": [],
                    "confidence_update": state.confidence_level + 0.1,
                    "should_continue": state.iteration_count < state.max_iterations
                }
            
            return Reflection(
                quality_assessment=reflection_data.get("quality_assessment", "medium"),
                new_insights=reflection_data.get("new_insights", []),
                remaining_questions=reflection_data.get("remaining_questions", []),
                suggested_pivots=reflection_data.get("suggested_pivots", []),
                confidence_update=min(reflection_data.get("confidence_update", state.confidence_level), 1.0),
                should_continue=reflection_data.get("should_continue", True)
            )
            
        except Exception as e:
            print(f"Error parsing reflection response: {e}")
            # Return default reflection
            return Reflection(
                quality_assessment="medium",
                new_insights=[],
                remaining_questions=[],
                suggested_pivots=[],
                confidence_update=min(state.confidence_level + 0.1, 1.0),
                should_continue=state.iteration_count < state.max_iterations
            )


@dataclass
class DeepResearchConfig(ModelConfig):
    """Configuration for DeepResearchAgent."""
    
    # Inherited from ModelConfig
    # model: str = "claude-3-sonnet-20240229"
    # max_tokens: int = 4096
    # temperature: float = 1.0
    # context_window_tokens: int = 180000
    
    # Research-specific config
    enable_sources: List[str] = field(default_factory=lambda: ["web", "google_drive"])
    research_depth: str = "balanced"  # 'shallow', 'balanced', 'deep'
    max_sources_per_query: int = 2
    enable_caching: bool = True
    cache_duration: int = 3600  # 1 hour
    enable_research_memory: bool = True
    correlation_threshold: float = 0.7
    verbose: bool = True


class DeepResearchAgent:
    """Research agent with ReAct framework for intelligent multi-source research."""
    
    def __init__(
        self,
        name: str = "DeepResearchAgent",
        config: Optional[DeepResearchConfig] = None,
        client: Optional[Anthropic] = None,
    ):
        """Initialize the DeepResearchAgent."""
        self.name = name
        self.config = config or DeepResearchConfig()
        self.client = client or Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "")
        )
        
        # Initialize reasoning engine
        self.reasoning_engine = ReActReasoningEngine(self.client, self.config.model)
        
        # Initialize tools based on enabled sources
        self.tools = self._initialize_tools()
        self.tool_dict = {tool.name: tool for tool in self.tools}
        
        # Initialize message history for synthesis
        self.history = MessageHistory(
            model=self.config.model,
            system=self._get_synthesis_prompt(),
            context_window_tokens=self.config.context_window_tokens,
            client=self.client,
        )
        
        if self.config.verbose:
            print(f"\n[{self.name}] Initialized with sources: {self.config.enable_sources}")
            self._check_api_keys()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools based on enabled sources."""
        tools = []
        
        if "web" in self.config.enable_sources:
            tools.extend([BraveSearchTool(), FirecrawlContentTool()])
        
        if "google_drive" in self.config.enable_sources:
            tools.extend([GoogleDriveTool(), GoogleDriveContentTool(self.client)])
        
        return tools
    
    def _check_api_keys(self):
        """Check if API keys are properly configured."""
        print(f"🔑 API Key Status:")
        print(f"   Anthropic: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'}")
        
        if "web" in self.config.enable_sources:
            print(f"   Brave Search: {'✅' if os.getenv('BRAVE_SEARCH_API_KEY') else '❌ (fallback available)'}")
            print(f"   Firecrawl: {'✅' if os.getenv('FIRECRAWL_API_KEY') else '❌ (fallback available)'}")
        
        if "google_drive" in self.config.enable_sources:
            gdrive_auth = (
                os.path.exists('token.pickle') or 
                os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE') or
                False  # Check for default credentials
            )
            print(f"   Google Drive: {'✅' if gdrive_auth else '❌'}")
    
    def _get_synthesis_prompt(self) -> str:
        """Get the system prompt for research synthesis."""
        return """You are a research synthesis expert. Your role is to:

1. Analyze findings from multiple sources
2. Identify key themes and patterns
3. Resolve contradictions between sources
4. Provide a comprehensive, well-structured summary
5. Maintain source attribution for all claims

When synthesizing research:
- Prioritize recent and authoritative sources
- Highlight agreements and disagreements between sources
- Identify gaps in the available information
- Provide a balanced, objective perspective
- Use clear, concise language

Always cite sources using [Source: title] format."""
    
    async def _extract_objective(self, query: str) -> str:
        """Extract the research objective from the query."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=200,
            temperature=0.5,
            system="Extract the main research objective from the query in one clear sentence.",
            messages=[
                {"role": "user", "content": query}
            ]
        )
        return response.content[0].text.strip()
    
    async def _execute_tool_calls(
        self,
        source_type: str,
        queries: List[str]
    ) -> List[Finding]:
        """Execute tool calls for a specific source."""
        findings = []
        
        # Map source types to tool names
        tool_mapping = {
            "web": "brave_search",
            "google_drive": "google_drive_search"
        }
        
        tool_name = tool_mapping.get(source_type)
        if not tool_name or tool_name not in self.tool_dict:
            return findings
        
        tool = self.tool_dict[tool_name]
        
        for query in queries:
            try:
                if self.config.verbose:
                    print(f"\n[{self.name}] Executing {tool_name}(query='{query}')")
                
                # Execute the tool
                result = await tool.execute(query=query)
                
                # Parse results into findings
                finding = Finding(
                    content=result,
                    source_type=SourceType(source_type),
                    source_url=None,
                    source_title=f"{source_type} search: {query}",
                    timestamp=datetime.now(),
                    relevance_score=0.8  # Default score, could be enhanced
                )
                findings.append(finding)
                
                # If web search returned URLs, optionally extract content
                if source_type == "web" and "firecrawl_extract" in self.tool_dict:
                    urls = self._extract_urls_from_search(result)
                    for url in urls[:2]:  # Extract top 2 URLs
                        if self.config.verbose:
                            print(f"[{self.name}] Extracting content from: {url}")
                        
                        content_result = await self.tool_dict["firecrawl_extract"].execute(url=url)
                        
                        content_finding = Finding(
                            content=content_result,
                            source_type=SourceType.WEB,
                            source_url=url,
                            source_title=f"Web content from {url}",
                            timestamp=datetime.now(),
                            relevance_score=0.9
                        )
                        findings.append(content_finding)
                
                # If Google Drive search returned file IDs, optionally extract content
                if source_type == "google_drive" and "google_drive_extract" in self.tool_dict:
                    file_ids = self._extract_file_ids_from_search(result)
                    for file_id in file_ids[:2]:  # Extract top 2 files
                        if self.config.verbose:
                            print(f"[{self.name}] Extracting content from file: {file_id}")
                        
                        content_result = await self.tool_dict["google_drive_extract"].execute(file_id=file_id)
                        
                        content_finding = Finding(
                            content=content_result,
                            source_type=SourceType.GOOGLE_DRIVE,
                            source_url=f"gdrive://{file_id}",
                            source_title=f"Google Drive file: {file_id}",
                            timestamp=datetime.now(),
                            relevance_score=0.9
                        )
                        findings.append(content_finding)
                
            except Exception as e:
                print(f"❌ Error executing {tool_name}: {str(e)}")
        
        return findings
    
    def _extract_urls_from_search(self, search_result: str) -> List[str]:
        """Extract URLs from search results."""
        urls = []
        lines = search_result.split('\n')
        for line in lines:
            if '🔗 URL:' in line:
                url = line.split('🔗 URL:')[1].strip()
                if url and url.startswith('http'):
                    urls.append(url)
        return urls
    
    def _extract_file_ids_from_search(self, search_result: str) -> List[str]:
        """Extract Google Drive file IDs from search results."""
        file_ids = []
        lines = search_result.split('\n')
        for line in lines:
            if '🆔 ID:' in line:
                file_id = line.split('🆔 ID:')[1].strip()
                if file_id:
                    file_ids.append(file_id)
        return file_ids
    
    def _update_state(self, state: ResearchState, reflection: Reflection) -> ResearchState:
        """Update research state based on reflection."""
        state.confidence_level = reflection.confidence_update
        state.gaps_identified = reflection.remaining_questions
        state.next_steps = reflection.suggested_pivots if reflection.suggested_pivots else ["continue"]
        
        # Add new insights to a metadata field (could be enhanced)
        for insight in reflection.new_insights:
            if self.config.verbose:
                print(f"💡 New insight: {insight}")
        
        return state
    
    async def _synthesize_research(self, state: ResearchState) -> ResearchReport:
        """Synthesize all findings into a final report."""
        # Prepare findings summary for synthesis
        findings_text = "Research Findings:\n\n"
        
        # Group findings by source
        by_source = {}
        for finding in state.current_findings:
            source = finding.source_type.value
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(finding)
        
        # Format findings by source
        for source, findings in by_source.items():
            findings_text += f"\n## From {source}:\n"
            for i, finding in enumerate(findings, 1):
                findings_text += f"\n{i}. "
                if finding.source_title:
                    findings_text += f"**{finding.source_title}**\n"
                # Truncate long content
                content_preview = finding.content[:500] + "..." if len(finding.content) > 500 else finding.content
                findings_text += f"{content_preview}\n"
        
        # Call LLM to synthesize
        synthesis_prompt = f"""
Research Query: {state.query}
Research Objective: {state.objective}

{findings_text}

Please provide a comprehensive synthesis of these findings that:
1. Answers the original query
2. Integrates information from all sources
3. Highlights key insights
4. Notes any contradictions or gaps
5. Provides a clear conclusion
"""
        
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=2000,
            temperature=0.7,
            system=self._get_synthesis_prompt(),
            messages=[
                {"role": "user", "content": synthesis_prompt}
            ]
        )
        
        synthesis = response.content[0].text
        
        return ResearchReport(
            query=state.query,
            objective=state.objective,
            findings=state.current_findings,
            synthesis=synthesis,
            confidence_level=state.confidence_level,
            sources_consulted=state.sources_consulted,
            iterations_performed=state.iteration_count,
            timestamp=datetime.now()
        )
    
    async def conduct_research(self, query: str) -> ResearchReport:
        """Main research loop using ReAct framework."""
        
        if self.config.verbose:
            print(f"\n🔍 Starting Deep Research for: {query}")
            print("=" * 60)
        
        # Initialize research state
        state = ResearchState(
            query=query,
            objective=await self._extract_objective(query),
            current_findings=[],
            sources_consulted={},
            confidence_level=0.0,
            gaps_identified=[],
            next_steps=["initial_search"],
            iteration_count=0
        )
        
        # ReAct loop
        while state.should_continue():
            iteration_num = state.iteration_count + 1
            if self.config.verbose:
                print(f"\n📍 Iteration {iteration_num}/{state.max_iterations}")
                print("-" * 40)
            
            # THINK: Reason about next steps
            if self.config.verbose:
                print("🤔 THINKING about next steps...")
            
            thought = await self.reasoning_engine.think(
                state, 
                self.config.enable_sources
            )
            
            if self.config.verbose:
                print(f"💭 Analysis: {thought.analysis}")
                print(f"📊 Confidence: {thought.confidence_assessment:.2f}")
                print(f"🎯 Recommended sources: {list(thought.recommended_sources.keys())}")
            
            # ACT: Execute recommended actions
            new_findings = []
            for source, queries in thought.recommended_queries.items():
                if source in self.config.enable_sources:
                    if self.config.verbose:
                        print(f"\n🔧 ACTING on {source} with {len(queries)} queries")
                    
                    findings = await self._execute_tool_calls(source, queries)
                    new_findings.extend(findings)
                    
                    # Track queries
                    if source not in state.sources_consulted:
                        state.sources_consulted[source] = []
                    state.sources_consulted[source].extend(queries)
            
            # OBSERVE: Add new findings to state
            state.current_findings.extend(new_findings)
            
            if self.config.verbose:
                print(f"\n👀 OBSERVING: Found {len(new_findings)} new pieces of information")
            
            # REFLECT: Evaluate progress and update strategy
            if self.config.verbose:
                print("\n🔍 REFLECTING on findings...")
            
            reflection = await self.reasoning_engine.reflect(state, new_findings)
            
            if self.config.verbose:
                print(f"📈 Quality: {reflection.quality_assessment}")
                print(f"🎯 New confidence: {reflection.confidence_update:.2f}")
                print(f"❓ Remaining questions: {len(reflection.remaining_questions)}")
                print(f"➡️  Continue: {reflection.should_continue}")
            
            # Update state based on reflection
            state = self._update_state(state, reflection)
            state.iteration_count += 1
            
            # Check if we should stop based on reflection
            if not reflection.should_continue:
                if self.config.verbose:
                    print("\n✅ Research complete based on reflection")
                break
        
        # Synthesize final report
        if self.config.verbose:
            print("\n📝 SYNTHESIZING final research report...")
        
        report = await self._synthesize_research(state)
        
        if self.config.verbose:
            print(f"\n✨ Research completed!")
            print(f"📊 Final confidence: {report.confidence_level:.2f}")
            print(f"🔄 Iterations performed: {report.iterations_performed}")
            print(f"📚 Sources consulted: {list(report.sources_consulted.keys())}")
        
        return report
    
    def run(self, query: str) -> ResearchReport:
        """Synchronous wrapper for conduct_research."""
        return asyncio.run(self.conduct_research(query))


def main():
    """Example usage of the DeepResearchAgent."""
    
    # Initialize the agent
    config = DeepResearchConfig(
        enable_sources=["google_drive"],
        research_depth="balanced",
        verbose=True
    )
    
    agent = DeepResearchAgent(config=config)
    
    # Example queries
    queries = [
        "How many I797 Approval notices do I have and what is their information",
        # "Find information about our Q4 marketing strategy",  # Would search Google Drive
        # "What are the best practices for Python async programming?",
    ]
    
    print("🚀 Deep Research Agent Demo")
    print("=" * 60)
    
    for query in queries:
        print(f"\n🔍 Researching: {query}")
        print("-" * 60)
        
        try:
            report = agent.run(query)
            
            print(f"\n📄 FINAL REPORT")
            print("=" * 60)
            print(f"Query: {report.query}")
            print(f"Objective: {report.objective}")
            print(f"Confidence: {report.confidence_level:.2%}")
            print(f"Sources: {', '.join(report.sources_consulted.keys())}")
            print(f"\n📝 Synthesis:")
            print("-" * 40)
            print(report.synthesis)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main() 