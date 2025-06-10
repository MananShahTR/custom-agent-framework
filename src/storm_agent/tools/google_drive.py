"""Google Drive tools for agents."""

import os
import pickle
import base64
import io
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from anthropic import Anthropic

from .base import Tool
from ..utils.approval import require_approval


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
        # Method 1: OAuth2 token (for user authentication) - look in project root
        token_paths = [
            'token.pickle',  # Project root
            '../token.pickle',  # One level up
            '../../token.pickle'  # Two levels up
        ]
        
        for token_path in token_paths:
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                    if self.verbose if hasattr(self, 'verbose') else True:
                        print(f"✅ Found Google Drive token at: {token_path}")
                    break
                except Exception as e:
                    if self.verbose if hasattr(self, 'verbose') else True:
                        print(f"⚠️  Could not load token from {token_path}: {e}")
                    continue
        
        # Method 2: Service account (for server applications)
        if not creds:
            service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            if service_account_file and os.path.exists(service_account_file):
                try:
                    creds = service_account.Credentials.from_service_account_file(
                        service_account_file,
                        scopes=['https://www.googleapis.com/auth/drive.readonly']
                    )
                    if self.verbose if hasattr(self, 'verbose') else True:
                        print(f"✅ Found Google Drive service account at: {service_account_file}")
                except Exception as e:
                    if self.verbose if hasattr(self, 'verbose') else True:
                        print(f"⚠️  Could not load service account from {service_account_file}: {e}")
        
        # Method 3: Application default credentials (only try if likely to work)
        if not creds:
            # Only try application default credentials if we're likely in a cloud environment
            try:
                # Check if we're in a cloud environment by looking for common env vars
                cloud_env_vars = [
                    'GOOGLE_CLOUD_PROJECT',
                    'GCLOUD_PROJECT', 
                    'GOOGLE_APPLICATION_CREDENTIALS',
                    'CLOUDSDK_CORE_PROJECT'
                ]
                
                is_cloud_env = any(os.getenv(var) for var in cloud_env_vars)
                
                if is_cloud_env:
                    from google.auth import default
                    try:
                        creds, _ = default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
                        if self.verbose if hasattr(self, 'verbose') else True:
                            print("✅ Found Google Drive application default credentials")
                    except Exception as e:
                        # This is expected if not on GCE or no application default creds
                        if self.verbose if hasattr(self, 'verbose') else True:
                            print(f"⚠️  Application default credentials failed: {e}")
                else:
                    if self.verbose if hasattr(self, 'verbose') else True:
                        print("⚠️  Skipping application default credentials (not in cloud environment)")
                        
            except (ImportError, Exception) as e:
                # Skip application default credentials if they cause issues
                if self.verbose if hasattr(self, 'verbose') else True:
                    print(f"⚠️  Could not try application default credentials: {e}")
        
        if not creds:
            print("⚠️  Google Drive credentials not found.")
            print("   Checked locations:")
            for path in token_paths:
                print(f"   - {path}")
            print(f"   - Environment variable: GOOGLE_SERVICE_ACCOUNT_FILE")
            print("   - Application default credentials")
            return None
        
        try:
            service = build('drive', 'v3', credentials=creds)
            if self.verbose if hasattr(self, 'verbose') else True:
                print("✅ Google Drive service initialized successfully")
            return service
        except Exception as e:
            print(f"⚠️  Could not initialize Google Drive service: {str(e)}")
            return None
    
    
    async def execute(
        self, 
        query: str, 
        file_types: List[str] = None,
        max_results: int = 10,
        order_by: str = "modifiedTime"
    ) -> str:
        """Search Google Drive and return formatted results."""
        if not self.service:
            return """❌ Google Drive service not available. 

To use Google Drive tools, you need to set up authentication:

**Option 1: OAuth2 (Recommended for personal use)**
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a project or select existing one
3. Enable Google Drive API
4. Create OAuth2 credentials (Desktop application)
5. Download the credentials file as 'credentials.json'
6. Run the authentication flow to generate 'token.pickle'

**Option 2: Service Account (For server applications)**
1. Create a service account in Google Cloud Console
2. Download the service account key file
3. Set environment variable: GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/key.json

**Option 3: Skip Google Drive**
- The research agent can work with web sources only
- Disable Google Drive in the configuration

For now, continuing with web-only research..."""
        
        try:
            # Build the search query
            search_query = self._build_search_query(query, file_types)
            
            # Execute search
            results = self.service.files().list(
                q=search_query,
                pageSize=max_results,
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
    
    # @require_approval("Extract and read content from a Google Drive file")
    async def execute(self, file_id: str, export_format: str = "text/plain") -> str:
        """Extract content from a Google Drive file."""
        if not self.service:
            return """❌ Google Drive service not available. 

To extract content from Google Drive files, you need to set up authentication first.
See the google_drive_search tool error message for setup instructions.

For now, this operation cannot be completed without Google Drive access."""
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="name, mimeType, size, modifiedTime"
            ).execute()
            
            file_name = file_metadata.get('name', 'Unknown')
            mime_type = file_metadata.get('mimeType', '')
            
            print(f"\n🔍 EXTRACTING CONTENT FROM: {file_name}")
            print(f"📋 File Type: {mime_type}")
            print(f"📅 Modified: {file_metadata.get('modifiedTime', 'Unknown')[:10]}")
            print("=" * 80)
            
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
            
            # Print the extracted content for debugging
            print("📄 EXTRACTED CONTENT:")
            print("-" * 80)
            print(content)
            print("-" * 80)
            print("END OF EXTRACTED CONTENT\n")
            
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
            file_bytes = file_content.read()
            
            # Try to extract content based on file type
            if 'pdf' in mime_type.lower():
                return self._extract_pdf_content(file_bytes)
            elif 'word' in mime_type.lower() or 'msword' in mime_type.lower():
                return self._extract_document_content(file_bytes, mime_type)
            elif 'text' in mime_type:
                try:
                    return file_bytes.decode('utf-8', errors='ignore')
                except:
                    return "Could not decode text file"
            else:
                return self._extract_with_anthropic(file_bytes, mime_type)
            
        except Exception as e:
            return f"Error downloading file content: {str(e)}"
    
    def _extract_pdf_content(self, file_bytes: bytes) -> str:
        """Extract content from PDFs using PyPDF2, with Claude Sonnet fallback."""
        try:
            import PyPDF2
            import io
            
            # Create a PDF reader from bytes
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            
            # Extract text from all pages
            text_content = []
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text_content.append(f"=== Page {page_num + 1} ===\n{page_text}")
                except Exception as e:
                    text_content.append(f"=== Page {page_num + 1} ===\n[Error extracting page: {e}]")
            
            # Check if we got meaningful content
            combined_text = "\n\n".join(text_content)
            
            # If no content or very little content, try Claude fallback
            if not text_content or len(combined_text.strip()) < 50:
                print("⚠️  PyPDF2 extraction failed or returned minimal content. Trying Claude Sonnet...")
                return self._extract_pdf_with_claude(file_bytes, total_pages)
            
            # Truncate if too long
            max_length = 8000
            if len(combined_text) > max_length:
                combined_text = combined_text[:max_length] + "\n\n... (content truncated due to length)"
            
            return f"📕 **PDF Content Extracted** ({total_pages} pages)\n\n{combined_text}"
            
        except ImportError:
            # If PyPDF2 is not installed, try Claude directly
            print("⚠️  PyPDF2 not available. Trying Claude Sonnet extraction...")
            return self._extract_pdf_with_claude(file_bytes, "unknown")
            
        except Exception as e:
            # If PyPDF2 fails, try Claude fallback
            print(f"⚠️  PyPDF2 failed: {e}. Trying Claude Sonnet...")
            return self._extract_pdf_with_claude(file_bytes, "unknown")
    
    def _extract_pdf_with_claude(self, file_bytes: bytes, total_pages) -> str:
        """Extract PDF content using Claude Sonnet when PyPDF2 fails."""
        try:
            size_mb = len(file_bytes) / (1024 * 1024)
            
            # Check file size (Claude has limits)
            if size_mb > 10:  # 10MB limit for safety
                return f"""📕 **PDF Too Large for Claude Extraction**

PDF file size: {size_mb:.1f} MB (exceeds 10MB limit)

The PDF is too large to send to Claude for text extraction. Options:
1. Convert the PDF to a smaller file
2. Convert to Google Docs format for better extraction
3. Use an online PDF to text converter
4. Split the PDF into smaller sections"""

            # Encode PDF as base64
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            
            # Create message for Claude
            message_content = [
                {
                    "type": "text",
                    "text": """Please extract all text content from this PDF document. Focus on:
1. All readable text, numbers, and data
2. Preserve the structure and formatting as much as possible
3. Include any forms, tables, or structured data
4. Note any sections that appear to be handwritten or unclear

Please provide the extracted text in a clear, organized format."""
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
            
            # Call Claude to extract content
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )
            
            # Extract the text content from Claude's response
            claude_text = ""
            if hasattr(response, 'content') and response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        claude_text += content_block.text
            
            if claude_text.strip():
                return f"""📕 **PDF Content Extracted via Claude Sonnet** ({total_pages} pages, {size_mb:.1f} MB)

🤖 Note: This PDF was processed using Claude Sonnet as it contains scanned/image content that couldn't be extracted with standard text extraction.

{claude_text}"""
            else:
                return f"""📕 **PDF Content Extraction Failed**

File size: {size_mb:.1f} MB, Pages: {total_pages}

Both PyPDF2 and Claude Sonnet were unable to extract readable text from this PDF. This might be because:
1. The PDF contains only images without OCR text
2. The PDF is corrupted or password protected  
3. The content is in a format that's difficult to process

Suggestions:
- Try converting the PDF to a searchable PDF using OCR
- Convert to Google Docs format
- Use a dedicated OCR tool"""
                
        except Exception as e:
            size_mb = len(file_bytes) / (1024 * 1024)
            return f"""❌ **Error with Claude PDF extraction** ({size_mb:.1f} MB): {str(e)}

Both PyPDF2 and Claude extraction failed. This PDF may be:
- Too complex or corrupted
- Password protected
- Contains only non-text content

Try converting the PDF to a text format or Google Docs."""
    
    def _extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        """Extract content from Word documents."""
        try:
            # For Word documents, we would typically use python-docx or similar
            # For now, return a placeholder
            size_mb = len(file_bytes) / (1024 * 1024)
            return f"📄 Document content extraction is limited. File size: {size_mb:.1f} MB. Consider converting to Google Docs format for better extraction."
        except Exception as e:
            return f"Error extracting document content: {str(e)}"
    
    def _extract_with_anthropic(self, file_bytes: bytes, mime_type: str) -> str:
        """Generic extraction using Anthropic for unsupported file types."""
        try:
            size_mb = len(file_bytes) / (1024 * 1024)
            return f"📎 File type '{mime_type}' is not directly supported. File size: {size_mb:.1f} MB. Consider converting to a supported format."
        except Exception as e:
            return f"Error with generic extraction: {str(e)}" 