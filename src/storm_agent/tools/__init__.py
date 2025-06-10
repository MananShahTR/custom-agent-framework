"""Tool implementations."""

from .base import Tool
from .web_search import BraveSearchTool, FirecrawlContentTool
from .google_drive import GoogleDriveTool, GoogleDriveContentTool
from .handoff import HandoffTool, HandoffLogger
from .approval import RequestApprovalTool

try:
    from .mcp_tool import MCPTool
    __all__ = [
        "Tool", 
        "BraveSearchTool", 
        "FirecrawlContentTool",
        "GoogleDriveTool",
        "GoogleDriveContentTool",
        "HandoffTool",
        "HandoffLogger",
        "RequestApprovalTool",
        "MCPTool"
    ]
except ImportError:
    # MCP dependencies not available
    __all__ = [
        "Tool", 
        "BraveSearchTool", 
        "FirecrawlContentTool",
        "GoogleDriveTool",
        "GoogleDriveContentTool",
        "HandoffTool",
        "HandoffLogger",
        "RequestApprovalTool"
    ] 